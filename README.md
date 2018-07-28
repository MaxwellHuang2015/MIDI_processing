# 用法简介
## 由于辣鸡OSX系统带来的文件夹预处理操作

**文件夹由于经过辣鸡Mac的OSX系统，而会在windows及linux系统下多出来一堆._文件，处理前需要进行删除 呵呵呵呵呵**
> python delete.py --folder ***

## midi处理
**保留指定文件几类乐器音轨**
> python midi_precess.py --midi_file **** --hold piano drum

**去除指定文件几类乐器音轨**
> python midi_precess.py --midi_file **** --exclude piano drum

**保留指定文件夹下所有midi文件几类乐器音轨**
> python midi_precess.py --midi_folder **** --hold piano drum

**去除指定文件夹下所有midi文件几类乐器音轨**
> python midi_precess.py --midi_folder **** --exclude piano drum

**分析单个文件的乐器种类以及时长**

*该功能可能会有python-midi库中bug带来的bug，但是出错率可忍受，暂时不作处理*
> python midi_precess.py --midi_file **** --analyze 1

**分析指定文件夹下所有midi文件的乐器种类以及时长**

最后的分析结果会在当前路径下生成一个folder_analyze_0.csv文件，记录每个midi文件的路径以及对应的时长。

*该功能可能会有python-midi库中bug带来的bug，但是出错率可忍受，暂时不作处理*
> python midi_precess.py --midi_folder **** --analyze 1

**检测单个文件是否有指定的几类乐器**
> python midi_precess.py --check piano drum  --midi_file *****

**检测指定文件夹下所有的mid文件是否有指定的几类乐器**
> python midi_precess.py --check piano drum --midi_folder *****

最后的分析结果会在当前路径下生成一个['piano','drum']_0_check.csv文件，记录每个包含有piano和drum乐器的midi文件的路径以及对应的时长。

*该功能可能会有python-midi库中bug带来的bug，但是出错率可忍受，暂时不作处理*

**对超过一定长度的midi文件进行剔除**

在进行文件夹的分析检测时候，可以跟上一个长度阈值参数，那么文件夹下时长超过阈值的midi文件将不会被记录到csv文件中，从而达到剔除的效果。注意该参数的单位是秒。如：
> python midi_precess.py --check piano drum --midi_folder ***** --length_filter 100

那么最终会生成一个['piano','drum']_100_check.csv文件，其中记录了所有的包含有piano和drum两种乐器，并且时长不超过100s的midi文件的路径以及对应的时长。同理：
> python midi_precess.py --midi_folder **** --analyze 1 --length_filter 200

会生成一个folder_analyze_200.csv，记录了被分析的文件目录下所有的时长小于200s的midi文件的路径以及对应的时长。

# 需要的库的安装

## python-midi库

参考其[github](https://github.com/vishnubob/python-midi)

## tqdm库

> pip install tqdm

# 如出bug，请联系我解决（也许解决的了XD）