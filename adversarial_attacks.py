import OpenAttack
import transformers
import datasets
import os
import ssl
import torch
import pandas as pd
import re
from difflib import SequenceMatcher
import glob
from itertools import combinations
from OpenAttack import experiment_info
import gc

model_info = experiment_info.model_info
dataset_names = experiment_info.dataset_names
dataset_mappings = experiment_info.dataset_mappings

if torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"Using GPU:{torch.cuda.get_device_name(0)}")
else:
    device = torch.device("cpu")
    print("Using CPU")

ssl._create_default_https_context = ssl._create_unverified_context
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''


attacker_names = {
    "TextFooler": OpenAttack.attackers.TextFoolerAttacker(),
    "PWWS": OpenAttack.attackers.PWWSAttacker(),
    "TextBugger": OpenAttack.attackers.TextBuggerAttacker(),
    "HotFlip": OpenAttack.attackers.HotFlipAttacker(),
    "SCPN": OpenAttack.attackers.SCPNAttacker(),
    "GAN": OpenAttack.attackers.GANAttacker(),
}


def main():
    for model_name in model_info:
        print(f"Load model: {model_name}")
        model_config = model_info[model_name]
        tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)
        model = transformers.AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=model_config["num_labels"], output_hidden_states=False
        )
        model = model.to(device)
        embedding_layer = eval(f"model.{model_config['embedding_path']}")
        victim = OpenAttack.classifiers.TransformersClassifier(model, tokenizer, embedding_layer)

        print("New Attacker")
        attacker = attacker_names[attacker_name]
        print(f"Processing {attacker_name}")
        for subset, split in dataset_names[dataset_name].items():
            print(f"Processing {dataset_name}, Subset: {subset}")
            if subset in dataset_mappings[dataset_name]:
                mapping_function = dataset_mappings[dataset_name][subset]
            elif "default" in dataset_mappings[dataset_name]:
                mapping_function = dataset_mappings[dataset_name]["default"]
            else:
                raise ValueError(f"No mapping function found for dataset {dataset_name}, subset {subset}")
            dataset = datasets.load_dataset(dataset_name, subset, split=f"{split}[:100]").map(
                function=mapping_function)

        print("Start attack")
        attack_eval = OpenAttack.AttackEval(attacker, victim, metrics = [
            OpenAttack.metric.EditDistance(),
            OpenAttack.metric.ModificationRate()
        ])
        attack_eval.eval(dataset, model_name=model_name, dataset_name=dataset_name,
                         attacker_name=attacker_name, visualize=True)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()


def split_text(text):
    return re.findall(r"\w+|[^\w\s]", text, re.UNICODE)


def find_modified_words(original, attacked):

    if pd.isnull(original) or pd.isnull(attacked):
        return '', ''


    original = original.lower()
    attacked = attacked.lower()

    words_original = split_text(original)
    words_attacked = split_text(attacked)


    matcher = SequenceMatcher(None, words_original, words_attacked)
    modified_original_words = []
    modified_attacked_words = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            modified_original_words.extend(words_original[i1:i2])
            modified_attacked_words.extend(words_attacked[j1:j2])

    return ' '.join(modified_original_words), ' '.join(modified_attacked_words)


def modified():

    base_directory = os.path.join("..", "log")
    directory = os.path.join(base_directory, attacker_name, dataset_name)
    pattern = os.path.join(directory, 'saved_samples_*.csv')


    for filename in glob.glob(pattern):
        df = pd.read_csv(filename)
        df['modified_original'], df['modified_attacked'] = zip(
            *df.apply(lambda row: find_modified_words(row['original'], row['attacked']), axis=1))


        modified_filename = os.path.join(directory, 'modified_' + os.path.basename(filename))
        df.to_csv(modified_filename, index=False)
        print(f"Processed and saved: {modified_filename}")


def compare(dataset_name):

    base_directory = os.path.join("..", "log")
    directory = os.path.join(base_directory, attacker_name, dataset_name)

    if not os.path.exists(directory):
        os.makedirs(directory)
    pattern = os.path.join(directory, 'modified_saved_samples_*.csv')
    files = list(glob.glob(pattern))


    stats = {
        'file_pair': [],
        'both_attack_failed': [],
        'one_success_one_failed': [],
        'both_success_different_words': [],
        'both_success_same_words_different_content': [],
        'both_success_same_words_same_content': []
    }


    for file1, file2 in combinations(files, 2):

        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)


        both_attack_failed = one_success_one_failed = both_success_different_words = 0
        both_success_same_words_different_content = both_success_same_words_same_content = 0


        for index, row1 in df1.iterrows():
            row2 = df2.iloc[index]


            if pd.isna(row1['attacked']) and pd.isna(row2['attacked']):
                both_attack_failed += 1

            elif pd.isna(row1['attacked']) != pd.isna(row2['attacked']):
                one_success_one_failed += 1

            elif row1['modified_original'] != row2['modified_original']:
                both_success_different_words += 1

            elif row1['modified_original'] == row2['modified_original'] and row1['modified_attacked'] != row2[
                'modified_attacked']:
                both_success_same_words_different_content += 1

            elif row1['modified_original'] == row2['modified_original'] and row1['modified_attacked'] == row2[
                'modified_attacked']:
                both_success_same_words_same_content += 1


        file_pair = f'{dataset_name}/{os.path.basename(file1)} vs {dataset_name}/{os.path.basename(file2)}'
        stats['file_pair'].append(file_pair)
        stats['both_attack_failed'].append(both_attack_failed)
        stats['one_success_one_failed'].append(one_success_one_failed)
        stats['both_success_different_words'].append(both_success_different_words)
        stats['both_success_same_words_different_content'].append(both_success_same_words_different_content)
        stats['both_success_same_words_same_content'].append(both_success_same_words_same_content)


    output_path = f'{directory}/comparison_statistics.csv'
    stats_df = pd.DataFrame(stats)
    stats_df.to_csv(output_path, index=False)


def compare_detail(dataset_name):
    base_directory = os.path.join("..", "log")
    directory = os.path.join(base_directory, attacker_name, dataset_name)
    pattern = os.path.join(directory, 'modified_saved_samples_*.csv')
    files = list(glob.glob(pattern))


    comparison_results = []


    for file1, file2 in combinations(files, 2):
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)


        for index, row1 in df1.iterrows():
            row2 = df2.iloc[index]
            result = {
                'file_pair': f'{dataset_name}/{os.path.basename(file1)} vs {dataset_name}/{os.path.basename(file2)}',
                'row_index': index,
                'comparison_result': ''
            }


            if pd.isna(row1['attacked']) and pd.isna(row2['attacked']):
                result['comparison_result'] = 'both_attack_failed'
            elif pd.isna(row1['attacked']) != pd.isna(row2['attacked']):
                result['comparison_result'] = 'one_success_one_failed'
            elif row1['modified_original'] != row2['modified_original']:
                result['comparison_result'] = 'both_success_different_words'
            elif row1['modified_original'] == row2['modified_original'] and row1['modified_attacked'] != row2[
                'modified_attacked']:
                result['comparison_result'] = 'both_success_same_words_different_content'
            elif row1['modified_original'] == row2['modified_original'] and row1['modified_attacked'] == row2[
                'modified_attacked']:
                result['comparison_result'] = 'both_success_same_words_same_content'

            comparison_results.append(result)


    output_path = f'{directory}/detailed_comparison_results.csv'
    comparison_df = pd.DataFrame(comparison_results)
    comparison_df.to_csv(output_path, index=False)


def cross_compare(dataset_name):
    base_directory = os.path.join("..", "log")
    directory = os.path.join(base_directory, attacker_name, dataset_name)
    pattern = os.path.join(directory, 'modified_saved_samples_*.csv')
    files = list(glob.glob(pattern))


    file_pairs = [f'{dataset_name}/{os.path.basename(file1)} vs {dataset_name}/{os.path.basename(file2)}' for file1, file2 in combinations(files, 2)]
    comparison_df = pd.DataFrame(columns=file_pairs)


    for file1, file2 in combinations(files, 2):
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
        file_pair = f'{dataset_name}/{os.path.basename(file1)} vs {dataset_name}/{os.path.basename(file2)}'


        for index, row1 in df1.iterrows():
            row2 = df2[df2['original'] == row1['original']].iloc[0]


            if pd.isna(row1['attacked']) and pd.isna(row2['attacked']):
                comparison_result = 'both_attack_failed'
            elif pd.isna(row1['attacked']) != pd.isna(row2['attacked']):
                comparison_result = 'one_success_one_failed'
            elif row1['modified_original'] != row2['modified_original']:
                comparison_result = 'both_success_different_words'
            elif row1['modified_original'] == row2['modified_original'] and row1['modified_attacked'] != row2[
                'modified_attacked']:
                comparison_result = 'both_success_same_words_different_content'
            elif row1['modified_original'] == row2['modified_original'] and row1['modified_attacked'] == row2[
                'modified_attacked']:
                comparison_result = 'both_success_same_words_same_content'


            comparison_df.at[index, file_pair] = comparison_result


    comparison_df.to_csv(os.path.join(directory, 'cross_comparison_analysis.csv'))


if __name__ == "__main__":
    for attacker_name in attacker_names:
        for dataset_name in dataset_names:
            main()
            modified()
            compare(dataset_name)
            compare_detail(dataset_name)
            cross_compare(dataset_name)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
