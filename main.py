# -*- coding: utf-8 -*-
# @Time  : 2020/2/16 15:19
# @Author :
# @Desc : ==============================================
# If this runs wrong,don't ask me,I don't know why;  ===
# If this runs right,thank god,and I don't know why. ===
# ======================================================
# @Project : LSTM_CRF_IE
# @FileName: main.py.py
# @Software: PyCharm
import argparse
import train
import predict


parser = argparse.ArgumentParser(description='BiLSTM-CRF for Chinese NER task')
parser.add_argument('--mode', type=str, default='predict', help='train/test/predict')
args = parser.parse_args()

if args.mode == 'predict':
    #predict.run()
    PER, LOC, ORG = predict.run('我在北京上北京大学', True)
    print(PER, LOC, ORG)
else:
    train.run(args.mode)

