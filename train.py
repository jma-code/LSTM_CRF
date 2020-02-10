# train model
import sys
import time
import tensorflow as tf
import argparse
import os
import numpy as np
import utils.config as cf
from model import BiLSTM_CRF
from data_process import sentence2id, read_dictionary, read_corpus,tag2label
from utils import train_utils
from tensorflow.contrib.crf import viterbi_decode

params = cf.ConfigTrain('train', 'config/params.conf')
params.load_config()

# Session configuration
os.environ['CUDA_VISIBLE_DEVICES'] = '2'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
config.gpu_options.per_process_gpu_memory_fraction = 0.3

## hyperparameters
parser = argparse.ArgumentParser(description='BiLSTM-CRF for Chinese NER task')
parser.add_argument('--train_data', type=str, default=params.trainData_path, help='train data source')
parser.add_argument('--test_data', type=str, default=params.testData_path, help='test data source')
parser.add_argument('--batch_size', type=int, default=params.batch_size, help='#sample of each minibatch')
parser.add_argument('--epoch', type=int, default=params.epoch, help='#epoch of training')
parser.add_argument('--hidden_dim', type=int, default=params.hidden_dim, help='#dim of hidden state')
parser.add_argument('--optimizer', type=str, default=params.optimizer, help='Adam/Adadelta/Adagrad/RMSProp/Momentum/SGD')
parser.add_argument('--lr', type=float, default=params.lr, help='learning rate')
parser.add_argument('--clip', type=float, default=params.clip, help='gradient clipping')
parser.add_argument('--dropout', type=float, default=params.dropout, help='dropout keep_prob')
parser.add_argument('--update_embedding', type=train_utils.str2bool, default=params.update_embedding, help='update embedding during training')
parser.add_argument('--pretrain_embedding', type=str, default='random', help='use pretrained char embedding or init it randomly')
parser.add_argument('--embedding_dim', type=int, default=params.embedding_dim, help='random init char embedding_dim')
parser.add_argument('--shuffle', type=train_utils.str2bool, default=params.shuffle, help='shuffle training data before each epoch')
parser.add_argument('--mode', type=str, default='demo', help='train/test/demo')
parser.add_argument('--demo_model', type=str, default='1521112368', help='model for test and demo')
args = parser.parse_args()


# 参数部分
embedding_mat = np.random.uniform(-0.25, 0.25, (4756, 300))  # 4756*300
embedding_mat = np.float32(embedding_mat)
embeddings = embedding_mat

num_tags = len(tag2label)
word2id = read_dictionary("data/word2id")
summary_path = "logs"
model_path = "checkpoints"
result_path = ''

train_data = read_corpus(args.train_data)
test_data = read_corpus(args.test_data)

# 模型加载
model = BiLSTM_CRF(embeddings, args.update_embedding, args.hidden_dim, num_tags, args.clip, summary_path, args.optimizer)
model.build_graph()


def dev_one_epoch(sess, dev):
    """

    :param sess:
    :param dev:
    :return:
    """
    # 需要predict方法
    pass


def run_one_epoch(sess, train, dev, tag2label, epoch, saver):
    num_batches = (len(train) + args.batch_size -1) // args.batch_size
    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    batches = train_utils.batch_yield(train, args.batch_size, word2id, tag2label)

    for step, (seqs, labels) in enumerate(batches):
        sys.stdout.write(' processing: {} batch / {} batches.'.format(step + 1, num_batches) + '\r')
        step_num = epoch * num_batches + step +1

        feed_dict, _ = train_utils.get_feed_dict(seqs, labels, args.lr, args.dropout)
        _, loss_train, summary, step_num_ = sess.run([model.train_op, model.loss, model.merged, model.global_step], feed_dict=feed_dict)
        if step + 1 == 1 or (step + 1) % 20 == 0 or step + 1 ==num_batches:
            print('logger info')
            print("{} epoch {}, step {}, loss:{:.4}, total_step:{}".format(start_time, epoch + 1, step + 1, loss_train, step_num))

        # 写入日志文件
        # logging.info()

        if step + 1 == num_batches:
            saver.sace(sess, model_path, global_step=step_num)

    label_list_dev, seq_len_list_dev = dev_one_epoch(sess, dev)

def evaluate(label_list, seq_len_list, data, epoch=None):
    """

    :param label_list:
    :param seq_len_list:
    :param data:
    :param epoch:
    :return:
    """
    label2tag = {}
    for tag, label in tag2label.items():
        label2tag[label] = tag if label != 0 else label

    model_predict = []
    for label_, (sent, tag) in zip(label_list, data):
        tag_ = [label2tag[label__] for label__ in label_]
        sent_res = []
        if  len(label_) != len(sent):
            print(sent)
            print(len(label_))
            print(tag)
        for i in range(len(sent)):
            sent_res.append([sent[i], tag[i], tag_[i]])
        model_predict.append(sent_res)
    epoch_num = str(epoch+1) if epoch != None else 'test'
    label_path = os.path.join(result_path, 'label_' + epoch_num)
    metric_path = os.path.join(result_path, 'result_metric_' + epoch_num)

def dev_one_epoch(sess, dev):
    """

    :param sess:
    :param dev:
    :return:
    """
    label_list, seq_len_list = [], []
    # 获取一个批次的句子中词的id以及标签
    for seqs, labels in data.batch_yield(dev, self.batch_size, self.vocab, tag2label, shuffle=False):
        feed_dict, seq_len_list_ = train_utils.get_feed_dict(seqs, drop_keep=1.0)
        logits, transition_params = sess.run([self.logits, self.transition_params],
                                             feed_dict=feed_dict)
        label_list_ = []
        for logit, seq_len in zip(logits, seq_len_list):
            viterbi_seq, _ = viterbi_decode(logit[:seq_len], transition_params)
            label_list_.append(viterbi_seq)


        label_list.extend(label_list_)
        seq_len_list.extend(seq_len_list_)
    return label_list, seq_len_list

def test(data):
    testSaver = tf.train.Saver()
    with tf.Session(config=config) as sess:
        testSaver.restore(sess, data)
        label_list, seq_len_list = dev_one_epoch(sess, data)
        evaluate(label_list, seq_len_list, data)

if args.mode == 'train':
    # model.train
    saver = tf.train.Saver(tf.global_variables())
    with tf.Session(config=config) as sess:
        tf.global_variables_initializer()  # 初始化模型参数
        model.add_summary(sess)
        for epoch in range(args.epoch):
            run_one_epoch(sess, train_data, test_data, tag2label, epoch, saver)

if args.mode == 'test':
    ckpt_file = tf.train.latest_checkpoint(model_path)
    test(test_data)

