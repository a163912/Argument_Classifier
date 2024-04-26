import argparse
#from mine_next.functions.main_function import train, evaluate
from mine_next.functions.stance_main_func import train, evaluate
import random, os
import numpy as np
import torch
from transformers import AutoConfig, AutoTokenizer
from mine_next.model.modeling import RobertaForClassification, RobertaForSTANCY, RobertaForStanceClassification
from mine_next.model.modeling import RobertaReflectGraphClassification
from mine_next.functions.sent_to_graph import get_cons_tag_vocab


def create_model(args):
    config = AutoConfig.from_pretrained(
        args.language_model,
        num_labels=args.num_labels,
        max_length=args.max_length,
        # local_files_only=True
    )
    tokenizer = AutoTokenizer.from_pretrained(args.language_model, do_lower_case=False, use_fast=False)
    setattr(config, 'cons_hidden_size', args.cons_hidden_size)
    setattr(config, 'cons_tag2id', args.cons_tag2id)
    model = RobertaForClassification.from_pretrained(
        args.language_model if args.init_weight else os.path.join(args.output_dir, "checkpoint-{}".format(args.checkpoint)),
        config=config,
        # local_files_only=True
    )
    return config, tokenizer, model

def set_seed(args):
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)

def main(args):
    set_seed(args)
    config, tokenizer, model = create_model(args)
    model.to(args.device)

    if args.mode == 'train':
        train(args, model, tokenizer)
    elif args.mode == 'dev':
        evaluate(args, model, tokenizer)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='main')
    parser.add_argument('--claim_train', type=str, default='../data/IAM/claims/train.txt')
    parser.add_argument('--claim_dev', type=str, default='../data/IAM/claims/dev.txt')
    parser.add_argument('--stance_train', type=str, default='../data/IAM/stance/train.txt')
    parser.add_argument('--stance_dev', type=str, default='../data/IAM/stance/dev.txt')
    parser.add_argument('--save_dir', type=str, default='stance_test') # 모델 불러올 dir
    parser.add_argument('--output_dir', type=str, default='stance_test') # 모델 저장할 dir
    parser.add_argument('--constituent_gold_vocab', type=str, default='../data/IAM/constituent_gold_vocab.txt')
    parser.add_argument('--init_weight', type=bool, default=True) # False면 학습된거. True면 쌩 로버타
    parser.add_argument('--device', type=str, default="cuda")
    #model
    parser.add_argument('--num_labels', type=int, default=2)
    parser.add_argument('--max_length', type=int, default=256)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--cons_tag2id', type=dict, default=get_cons_tag_vocab('../data/IAM/constituent_gold_vocab.txt'))
    parser.add_argument('--cons_hidden_size', type=int, default=128)

    parser.add_argument("--gradient_accumulation_steps", type=int, default=1)
    parser.add_argument("--learning_rate", type=float, default=3e-5)
    parser.add_argument("--warmup_steps", type=int, default=0)
    parser.add_argument("--max_grad_norm", type=float, default=5.0)
    parser.add_argument('--mode', type=str, default='train')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--checkpoint', type=int, default=1)
    parser.add_argument('--language_model', type=str, default='roberta-base')
    parser.add_argument("--epoch", type=int, default=15)

    args = parser.parse_args()
    main(args)
