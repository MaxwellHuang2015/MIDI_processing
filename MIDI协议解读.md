# MIDI协议解读

## [**何为MIDI**](https://en.wikipedia.org/wiki/MIDI)
**乐器数字接口**（Musical Instrument Digital Interface，简称**MIDI**）是一个工业标准的电子通信协议，为电子乐器等演奏设备（如合成器）定义各种音符或弹奏码，容许电子乐器、电脑、手机或其它的舞台演出配备彼此连接，调整和同步，得以即时交换演奏数据。简单而言，就是电子系统中的五线谱/简谱，用于数字化保存音乐的一种协议。
![launchpad][1]
目前绝大部分的电子乐器、合成器以及控制器等等都是使用的MIDI协议。
MIDI不发送声音，只发送像是音调和音乐强度的数据，音量，颤音和相位等参数的控制信号，还有设置节奏的时钟信号。在不同的电脑上，输出的声音也因音源器不同而有差异。所以前边用五线谱来形容他还是比较恰当的。

----------
## **MIDI协议**
>**注意：**不是所所有MIDI设备都能对所有的MIDI信息进行相应。
一般而言，MIDI中各类信息的值的范围都是0-127，也就是2^7 个，可以用7个bit进行表述。

### **MIDI信息组成**
MIDI信息其实就是由一个或多个字节构成的时间序列。第一个byte是**状态字节**，或者称为数据类型字节也可，用来表明后边跟随的数据对应的信息类型；状态字节之后一般会跟随着**数据字节**，用来表示前边定义的数据类型下具体数据。
**状态字节**和**数据字节**的区别在于：前者第一个bit是1，后者第一个bit是0。因此状态字节的范围是0x80-0xFF，而数据字节的范围是0x00-0x7F。
>**注意：**状态字节中的低四位，对应的数据代表的了通道值，也就是说：一个基本的MIDI信息可以记录下2^4 =16个通道的音乐信息，至于每个通道对应什么声音或者效果，由效果器/解析器的设置决定了。

### **MIDI表示的音乐信息**
**note-on和note-off**

note意思为音符，按下某个音符时，MIDI会用note-on信息来记录。
同理，note-off信息是用来记录音符停止的。

![note-on_note-off][2]

**velocity**

velocity信息记录的是某个音符产生的速度或者叫力度，可以参考钢琴琴键以不同力度按下的区别。一般而言，力度越大，对应的声音越大。

![velocity][3]

一般而言，在note-on信息中该值的范围是1-127，如果是0，那么其实效果与note-off信息是一样的，对应到乐谱中，强弱对应关系是：

![velocity—mapping][4]

**pitch**

pitch信息，即音符的音调信息。音调值以0-127总共128个进行量化，以中央C音为60，每个半音为1进行增减以表示音调，比如：C#音，升C音，也就是比C音高半个音，那么他是61，以此类推D音是62......
升/降一个八度在MIDI中的表示，因此就是将pitch值加/减12即可。

**aftertouch**

aftertouch信息，这个信息一般只会出现在按键类新的MIDI控制器中，记录的是某个音符（按键）再被按下的期间，你对这个按键的按压力度。

![aftertouch][5]

**program change**

该信息对应的是MIDI设备所要使用的乐器种类，或者又可以称为音色种类。

**control change**

该信息用来表示MIDI设备的一些操作控制信息，例如音色库的选择、音量调节等等。

### **[主要MIDI信息的结构](https://www.midi.org/specifications/category/reference-tables)**
**音符开始/结束**

一个**音符开始**被击发的MIDI信息如下（二进制）：

* 状态字节：1001 CCCC
* 数据字节1：0PPP PPPP
* 数据字节2：0VVV VVVV

其中：
    “CCCC”代表MIDI通道(0-15)；
    “PPP PPPP”对应的是pitch值，也就是音调(0-127)；
    “VVV VVVV”对应的是velocity值，也就是强度(0-127)；
    
那么**音符停止**的MIDI信息为：

* 状态字节：1000 CCCC
* 数据字节1：0PPP PPPP
* 数据字节2：0VVV VVVV

默认的，此时的velocity值为0。

**音色信息**

通过program change信息，可以告诉MIDI设备切换到想要的音色/发声效果。同样的，也是0-127的范围，总共有128中声音可选。如果没有向MIDI设备发送program change信息，那么设备将会以钢琴或者默认乐器对音符进行演奏。
通用的乐器库列表，也就是128种乐器对应的编号可以参考[通用MIDI标准表](https://www.midi.org/specifications/item/gm-level-1-sound-set)，又称为GM(General MIDI)。对应的MIDI信息格式为：

* 状态字节：1100 CCCC
* 数据字节：0XXX XXXX

那么事实上，声音效果或者声音种类肯定不止128种，因此还会有另一个信息control change用来选择“音色库”。

**控制信息**

通过control change信息，可以对MIDI设备进行一些控制，这些控制包括：选择音色库、调节音量大小、调节均衡器等等，具体的信息结构为：

* 状态字节：1011 CCCC
* 数据字节1：0NNN NNNN
* 数据字节2：0VVV VVVV

同样的，C代表的是通道值，N对应的是所要控制的属性的编号，而V对应的是控制的属性想要达到的值。具体的N也就是控制属性编号表格可以参考[控制属性编号表](https://www.midi.org/specifications/item/table-3-control-change-messages-data-bytes-2)。

**Pitch bend**

弯音信息，一般用于表示吉他的滑音之类的连续性的音调变化，因此需要比上边pitch信息更多的等级来描绘音调。
pitch bend信息格式为：

* 状态字节：1110 CCCC
* 数据字节1：0LLL LLLL
* 数据字节2：0MMM MMMM

一样的，CCCC代表的是MIDI的通道，LLL LLLL是pitch偏移值的LSB即低字节(少了一个bit，也就这么叫吧~)，MMM MMMM是MSB即高字节，合起来就是MM MMMM MLLL LLLL来表示音调的变化。注意！这里的值对应的是音调的升降值，而非某个特定的音调，也就是最后显示出来的声音，其实与对应的note的原本的pitch值有关。
一般而言，该信息的取值范围是0x0000~0x3FFF，对应的音调升降是-2~+2半音，也就是说0x2000对应的就是音调不变。

**和弦**

和弦一般会在同个时间有某几个音符同时产生，那么这种情况，MIDI是通过在文件中自带时间序列信息来解决的。举个例子，如果同时发C和D两个音，那么在带有时间序列的MIDI文件里头，会呈现出：
    
| 时隙  | 信息      |
| :---: | :----:    |
|   0   | C note on |
|   0   | D note on |
|   1   | C note off|
|   2   | D note off|

至于如何表示出时间信息，那么就得往后看MIDI文件的文件格式了。

具体更多的MIDI协议信息可以参考MIDI官网下的相关文章，例如[信息类型](https://www.midi.org/articles/about-midi-part-3-midi-messages)，以及相应的[编码表](https://www.midi.org/specifications/category/reference-tables)等。


----------
## **MIDI文件格式**
MIDI的标准文件后缀是.mid，基本上大部分音频软件都可以打开。其文件编码格式，暂时没有在MIDI官网找到，不过可以从这个[Wiki](https://github.com/colxi/midi-parser-js/wiki/MIDI-File-Format-Specifications)进行了解，亦或者通过[另一个Wiki](https://www.csie.ntu.edu.tw/~r92092/ref/midi/)进行补充了解。
大体来讲，MIDI文件分为两部分，文件头块（Header chunk）和音轨块（Track chunk）
。在介绍两个块之前，需要先介绍一下变长字段（Variable-length）的数据存储方式。

### **变长字段/Variable-length**
有些信息的存储，我们不想由于预定义的存储字节数而限制住数据的最大值，所以采取变长字段进行存储。变长字段的数据格式是：每个byte中的最高位bit，作为当前数据存储是否结束的符号，具体可以通过以下几个例子来了解：
<table>
    <tr>
        <th colspan="2">具体数值</th> 
        <th colspan="2">变长字段</th> 
    </tr>
    <tr>
        <td>十六进制Hex</td> 
        <td>二进制Bin</td>
        <td>十六进制Hex</td> 
        <td>二进制Bin</td>
    </tr>
    <tr>
        <td>08</td> 
        <td>00001000</td>
        <td>08</td> 
        <td>00001000</td>
    </tr>
    <tr>
        <td>C8</td> 
        <td>11001000</td>
        <td>8148</td> 
        <td>10000001 01001000</td>
    </tr>
    <tr>
        <td>100000</td> 
        <td>00010000 00000000 00000000</td>
        <td>C08000</td> 
        <td>11000000 10000000 00000000</td>
    </tr>
</table>

### **头块/Header chunk**
头块部分定义了MIDI文件的整体全局信息，包括：MIDI文件的格式类型、音轨数量以及时钟划分参数等等。一个MIDI文件中只有一个头块，并且头块一定是在文件的最开始。如果用文本编辑器打开MIDI文件，可以看到MIDI文件的十六进制编码，具体编码对应表可以看以下表格：

| 字节偏移量 | 长度 | 类型 | 描述 | 值 |
| :--: | :--: | :--: | :--: | :--: |
| 0x00 | 4 | char\[4] | 块ID | "MThd"(0x4D546864) |
| 0x04 | 4 | dword | 块大小 | 6(0x00000006) |
| 0x08 | 2 | word | MIDI文件格式类型 | 0/1/2 |
| 0x10 | 2 | word | 音轨数量 | 1~65,535 |
| 0x12 | 2 | word | 时钟划分参数 | 详见下文 |

其中
**块ID，块大小**

块ID固定是字符串"MThd"，块大小，也就是整个头块的占据的byte数量也是固定不变的，值为6。因此，一个MIDI文件最开头的8个byte一定会是：
4D 54 68 64 00 00 00 06

**MIDI文件格式类型**

MIDI文件格式有0/1/2三种：
0 —— 该MIDI文件只有一个音轨，所有的信息都是在一个音轨中；
1 —— 该MIDI文件有多个音轨，一般用法是第一个音轨保存该音乐的拍号啊、调号啊以及拍子之类的信息，后续音轨可能是他的标题或者作者，再后续包含各种乐器的音乐信息等等；
2 —— 这种类型是0类和1类的混合，这种音乐不同的音轨之间的序列并不一定是同步的，一般用来保存鼓类的？这个比较少见啦就不管他（大概）。

**音轨数量**

如果是0类的MIDI文件，那么这个值固定为1；如果是1类的MIDI文件，这个值的范围是2~65535。

**时钟划分参数**

该参数是用来定义MIDI文件中的“相对时间”(delta time)与现实世界中的时间的对应关系的。这个值对应的是：每个beat在MIDI中以多少个ticks表示，或者每一秒有多少帧。
如果该word的首位为0，也就是bitmask是0x8000，则接下来的该值为ticks per beat，也就是剩下的15个bits的数值，表示了该MIDI文件中，每一个拍子，会有多少个ticks。详细的需要参考下边的音轨块的内容。
如果该word的首位为1，也就是bitmask是0x7FFF，则是以帧/s的形式表示MIDI文件中的时间度量。这个比较骚，就不去说他了。

### **音轨块/Track chunk**
音轨块中大部分信息是按照上边的MIDI协议的信息，但是每个信息之前，都会有一个Delta-time，也就是时间相对量，代表的是接下来描述的这个事件，他和上一个事件之间的时间间隔，单位是头块中定义好的ticks。如果为0，那么意味着和上一个事件是同时发生的。哪些与时间不相关的信息，比如MIDI文件的标题啊，copyright这些，他们虽然在存储上保留着delta time，但是他们与时间无关，并且他们的delta time必须设定为0。具体形式为：

| Delta-time | 事件类型 | 通道/meta事件参数 |
| :---:    | :----:   | :----:   |
| 变长字段 | 4个bits  |  ... ... |

>**注意：** delta time是相对时间，也就是你在MIDI文件中直接读到的都是相对时间，如果要得到绝对时间，那么需要去计算。

具体哪些event对应设么记得参考上文的MIDI协议。这里不再赘述。值得注意的是，还有一类时间是叫meta事件，这类事件的用途是用来描述谱子的一些全局信息的。主要的几个meta事件的表格如下：

| Meta事件 | 事件类型 | 事件描述 | 备注 |
| :---:    | :----:   | :----:   | :----: |
|   0xff   | 0x2f     | 音轨结束 |
|   0xff   | 0x51     | 拍子设定 | 若没设置，则默认为120bpm |
|   0xff   | 0x58     | 拍号     | 默认4/4拍，24pqn，8 32nd |
|   0xff   | 0x59     | 调号     | 默认应该是C调 |    

  [1]: http://static.zybuluo.com/MaxwellHuang/lpq6du0ivfcrks3eq7mm9tqf/launchpad.jpg
  [2]: http://static.zybuluo.com/MaxwellHuang/84v4agyy0xfo5oghejg3oaqj/image_1ca7jq4lf11td1k2c1d39t3c1g099.png
  [3]: http://static.zybuluo.com/MaxwellHuang/coktrtdjkur8e4cilf1fpikt/image_1ca7kjru515fe11dc1pslp6clqum.png
  [4]: http://static.zybuluo.com/MaxwellHuang/b20p7utb9fw4utwclrkk5sap/image_1cao2hnvrmv71ssnl4ob2k6qu9.png
  [5]: http://static.zybuluo.com/MaxwellHuang/0d9ixfb6wa38qgofct6bj98n/image_1ca7ld9dplfpmsm1f4814gfllu13.png