from __future__ import division
from __future__ import print_function
import midi
import argparse
import glob
import os
import csv
from tqdm import tqdm
import multiprocessing
from functools import partial

MIDI_INSTRUMENT = ['piano', 'percussion', 'organ', 'guitar', 'bass', 'strings', 'ensemble', 'brass', 'reed', 'pipe', 'lead', 'pad', 'effects', 'ethnic', 'percussive', 'sound', 'drum']

def instrument_of_track(track):
    '''To clarify what kind of instruments
    in a track'''

    channels = []
    instruments = []

    for event in track:
        if event.name == 'Program Change':
            try:
                instruments.index(event.data[0])
                channels.index(event.channel)
            except ValueError:
                instruments.append(event.data[0])
                channels.append(event.channel)
                
    for event in track:
        if event.name =='Note On':
            if event.channel not in channels:
                channels.append(event.channel)
                if event.channel == 9:
                    instruments.append(128)
                else:
                    instruments.append(0)

    return channels, instruments

def instrument_of_pattern(track_list):
    '''To clarify what kind of instruments
    in a midi file'''

    channels = []
    instruments = []
    track_number = []

    count = 0
    for track in track_list:
        temp_ch, temp_instru = instrument_of_track(track)
        if len(temp_ch):
            channels = channels + temp_ch
            instruments = instruments + temp_instru
            for i in range(len(temp_ch)):
                track_number.append(count)
        count += 1

    return track_number, channels, instruments

def duration_of_pattern(track_list):
    '''To calculate the duration of
    a midi file'''

    tempo_list = []
    tempo_strart_tick = []
    ending_tick = []
    resolution = track_list.resolution
    track_list.make_ticks_abs()
    
    count = 0
    for track in track_list:
        note_count = 0
        ending_tick.append(track[-1].tick)
        for event in track:
            if event.name == 'Set Tempo':
                tempo_list.append(event.bpm)
                tempo_strart_tick.append(event.tick)
                count += 1
            elif event.name == 'Note On':
                note_count += 1
        if note_count == 0:
            ending_tick[-1] = 0
        
    if count == 0:
        tempo_list.append(120)
        tempo_strart_tick.append(0)
      
    true_end_tick = max(ending_tick)
    end = 0
        
    # print(tempo_strart_tick)
    # print(tempo_list)
    # print(resolution)
    # print(ending_tick)
    # print(true_end_tick)

    for i, val in enumerate(tempo_strart_tick):
        if i:
            end = end + 60*(val-tempo_strart_tick[i-1])/(resolution * tempo_list[i-1])
    end = end + 60*(true_end_tick-tempo_strart_tick[-1])/(resolution * tempo_list[-1])

    track_list.make_ticks_rel()
    return end

def delete_channel(track, channel):
    '''To delete certain channel'''

    new_track = midi.Track(tick_relative=False)
    for event in track:
        try:
            if event.channel != channel:
                new_track.append(event)
        except AttributeError:
            new_track.append(event)

    return new_track

def delete_track(track_list, index=-1, instrument=-1):
    '''To delete certain track with certain index
    or certain property like instrument'''
    
    if index<-1 and instrument<-1:
        print('Please claim what kind of track to delete')
    
    elif index>=0:
        try:
            track_list.pop(index)
            return track_list
        except ValueError:
            print('Index out of range')

    else:
        new_pattern = midi.Pattern()
        new_pattern.resolution = track_list.resolution
        for track in track_list:
            chan, instru = instrument_of_track(track)
            if len(chan) == 1:
                # print('1 channel '+str(chan))
                if chan[0] != 9 and (instru[0]//8 < len(MIDI_INSTRUMENT)) and (instru[0]//8 != instrument):
                    # print('1 track reserved')
                    new_pattern.append(track)
                elif chan[0] == 9 and instrument != MIDI_INSTRUMENT.index('drum'):
                    # print('1 track reserved')
                    new_pattern.append(track)

            elif len(chan):
                # print('serveral channel ' + str(chan))
                for i, ch in enumerate(chan):
                    if (instru[i]//8 == instrument) and (ch != 9):
                        # print('1 channel deleted')
                        track = delete_channel(track, ch)
                    elif (ch == 9) and (instrument == MIDI_INSTRUMENT.index('drum')):
                        # print('1 channel deleted')
                        track = delete_channel(track, ch)

                if len(track):
                    # print('1 track reserved')
                    new_pattern.append(track)

            else:
                # print('No channel')
                # The track is some kind of information track
                # print('1 track reserved')
                new_pattern.append(track)

        return new_pattern

def file_hold(file_path, instrument_list):
    '''Hold all the instruments claimed in 'instrument_list'
    and delete the others in the midi file whose path
    is 'file_path' '''

    if file_path[-4:] != ".mid" and file_path[-4:] != ".MID":
        print("Invalid midi file!")
        return

    else:
        output_name = file_path[0:-4] + '_processed.mid'

        pattern = midi.read_midifile(file_path)
        pattern.make_ticks_abs()

        if instrument_list[0] == 'all':
            print('~Nothing changed~')
            pattern.make_ticks_rel()
            midi.write_midifile(output_name, pattern)
            return

        else:
            hold_instru = []
            try: 
                for i in instrument_list:
                    hold_instru.append(MIDI_INSTRUMENT.index(i))

                for instru_index in range(len(MIDI_INSTRUMENT)):
                    if instru_index not in hold_instru:
                        pattern = delete_track(pattern, instrument=instru_index)
                
                pattern.make_ticks_rel()
                midi.write_midifile(output_name, pattern)

            except ValueError:
                print('Please select instrument among: ' + str(MIDI_INSTRUMENT))

def file_exclude(file_path, instrument_list):
    '''Delete all the instruments claimed in 'instrument_list'
    and hold the others in the midi file whose path
    is 'file_path' '''

    if file_path[-4:] != ".mid" and file_path[-4:] != ".MID":
        print("Invalid midi file!")
        return

    else:
        output_name = file_path[0:-4] + '_processed.mid'

        pattern = midi.read_midifile(file_path)
        pattern.make_ticks_abs()

        exclude_instru = []
        try: 
            for i in instrument_list:
                exclude_instru.append(MIDI_INSTRUMENT.index(i))

        except ValueError:
            print('Please select instrument among: ' + str(MIDI_INSTRUMENT))
            return

        for i in exclude_instru:
            pattern = delete_track(pattern, instrument=i)
        
        pattern.make_ticks_rel()
        midi.write_midifile(output_name, pattern)

def folder_hold(folder, instrument_list):
    '''Hold all the instruments claimed in 'instrument_list'
    and delete the others in all those legal midi file in folder
    whose path is 'folder' '''

    midi_file_list = []
    list_dirs = os.walk(folder)
    for root, dirs, files in list_dirs:
        for f in files:
            try:
                if f[-4:] == ".mid" or f[-4:] == ".MID":
                    midi_file_list.append(os.path.join(root, f))
            except :
                pass

    pbar = tqdm(total=len(midi_file_list))

    for midi_file in midi_file_list:
        file_hold(midi_file, instrument_list)
        pbar.update(1)
    pbar.close()

def folder_exclude(folder, instrument_list):
    '''Delete all the instruments claimed in 'instrument_list'
    and hold the others in all those legal midi file in folder
    whose path is 'folder' '''

    midi_file_list = []
    list_dirs = os.walk(folder)
    for root, dirs, files in list_dirs:
        for f in files:
            try:
                if f[-4:] == ".mid" or f[-4:] == ".MID":
                    midi_file_list.append(os.path.join(root, f))
            except :
                pass

    pbar = tqdm(total=len(midi_file_list))

    for midi_file in midi_file_list:
        file_exclude(midi_file, instrument_list)
        pbar.update(1)
    pbar.close()

def generate_report_csv():
    # TODO multiprocessing
    return 0

def folder_analyze(folder, length_filter=0):
    '''Show out the length of all the legal midi files 
    in the folder'''

    midi_file_list = []
    list_dirs = os.walk(folder)
    for root, dirs, files in list_dirs:
        for f in files:
            try:
                if f[-4:] == ".mid" or f[-4:] == ".MID":
                    midi_file_list.append(os.path.join(root, f))
            except :
                pass

    with open('folder_analyze_'+str(length_filter)+'.csv','wb') as myFile:
        myWriter=csv.writer(myFile)
        myWriter.writerow(["file_path", "length in second"])
        pbar = tqdm(total=len(midi_file_list))
        for midi_file in midi_file_list:
            try:
                pattern = midi.read_midifile(midi_file)
                length = duration_of_pattern(pattern)
                if length_filter:
                    if length <= length_filter:
                        myWriter.writerow([midi_file, length])
                else:
                    myWriter.writerow([midi_file, length])
            except :
                pass
            pbar.update(1)
    pbar.close()

def file_analyze(file_name):
    '''Show out the information of tracks, channels,
    instruments and length'''

    pattern = midi.read_midifile(file_name)
    track_number, channels, instruments = instrument_of_pattern(pattern)
    for i,val in enumerate(instruments):
        #print('Channel ' + str(channels[i]) + ' :' + MIDI_INSTRUMENT[instruments[i]//8])
        print('Track ' + str(track_number[i]) + ' Channel ' + str(channels[i]) + '\t' + str(instruments[i]))

    print(str(duration_of_pattern(pattern)) + " s" )

def file_check(file_name, instrument_list, print_out=True):
    '''Check out if all the instruments claimed in
    'instrument_list' exist in the midi file'''

    for i in instrument_list:
        if i not in MIDI_INSTRUMENT:
            print('Please select instrument among: ' + str(MIDI_INSTRUMENT))
            return -1

    pattern = midi.read_midifile(file_name)
    _, channels, instruments = instrument_of_pattern(pattern)
    for i,val in enumerate(instruments):
        if channels[i] != 9:
            instruments[i] = MIDI_INSTRUMENT[val//8]
    
    if print_out:
        print(instruments)
    
    lack_count = 0
    for i in instrument_list:
        if i == 'drum':
            if 9 not in channels:
                if print_out:
                    print(str(i) + " does not exist in " + file_name)
                lack_count += 1
        else:
            if i not in instruments:
                if print_out:
                    print(str(i) + " does not exist in " + file_name)
                lack_count += 1

    if lack_count:
        return 0

    else:
        if print_out:
            for i in instrument_list:
                print(i, end=" ")
            print("exist in " + file_name)
        return 1

def folder_check(folder, instrument_list, length_filter=0):
    '''Check out if all the instruments claimed in
    'instrument_list' exist in all those legal midi
    files under the folder and save the path of those 
    files that 'all exist' and whose length less than
    'length_filter' into a csv file'''

    for i in instrument_list:
        if i not in MIDI_INSTRUMENT:
            print('Please select instrument among: ' + str(MIDI_INSTRUMENT))
            return

    midi_file_list = []
    list_dirs = os.walk(folder)
    for root, dirs, files in list_dirs:
        for f in files:
            try:
                if f[-4:] == ".mid" or f[-4:] == ".MID":
                    midi_file_list.append(os.path.join(root, f))
            except :
                pass

    with open(str(instrument_list)+'_'+str(length_filter)+'_check.csv','wb') as myFile:
        myWriter=csv.writer(myFile)
        myWriter.writerow(["file_path", "length in second"])
        pbar = tqdm(total=len(midi_file_list))
        for midi_file in midi_file_list:
            try:
                if file_check(midi_file, instrument_list, print_out=False) == 1:
                    pattern = midi.read_midifile(midi_file)
                    length = duration_of_pattern(pattern)
                    if length_filter:
                        if length <= length_filter:
                            myWriter.writerow([midi_file, length])
                    else:
                        myWriter.writerow([midi_file, length])
            except :
                pass
            pbar.update(1)
    pbar.close()

def file_check_parallel(file_name, instrument_list, length_filter=0):
    '''Check out if all the instruments claimed in
    'instrument_list' exist in the midi file'''

    for i in instrument_list:
        if i not in MIDI_INSTRUMENT:
            print('Please select instrument among: ' + str(MIDI_INSTRUMENT))
            return

    try:
        pattern = midi.read_midifile(file_name)
        _, channels, instruments = instrument_of_pattern(pattern)
        for i,val in enumerate(instruments):
            if channels[i] != 9:
                instruments[i] = MIDI_INSTRUMENT[val//8]
        
        lack_count = 0
        for i in instrument_list:
            if i == 'drum':
                if 9 not in channels:
                    lack_count += 1
            else:
                if i not in instruments:
                    lack_count += 1

        if lack_count:
            return

        else:
            pattern = midi.read_midifile(file_name)
            length = duration_of_pattern(pattern)
            if length_filter:
                if length <= length_filter:
                    return file_name, length
                else:
                    return
            else:
                return file_name, length
    except :
        pass

def folder_check_parallel(folder, instrument_list, length_filter=0):
    '''Check out if all the instruments claimed in
    'instrument_list' exist in all those legal midi
    files under the folder and save the path of those 
    files that 'all exist' and whose length less than
    'length_filter' into a csv file'''

    for i in instrument_list:
        if i not in MIDI_INSTRUMENT:
            print('Please select instrument among: ' + str(MIDI_INSTRUMENT))
            return

    midi_file_list = []
    list_dirs = os.walk(folder)
    for root, dirs, files in list_dirs:
        for f in files:
            try:
                if f[-4:] == ".mid" or f[-4:] == ".MID":
                    midi_file_list.append(os.path.join(root, f))
            except :
                pass


    file_check_part = partial(file_check_parallel, instrument_list=instrument_list, length_filter=length_filter)
    pool = multiprocessing.Pool()
    result_list = list(tqdm(pool.imap_unordered(file_check_part, midi_file_list), total=len(midi_file_list)))
    with open(str(instrument_list)+'_'+str(length_filter)+'_check.csv','wb') as myFile:
        myWriter=csv.writer(myFile)
        myWriter.writerow(["file_path", "length in second"])
        for r in result_list:
            if r:
                myWriter.writerow(list(r))
                

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--midi_file', type=str, default='test.mid')
    parser.add_argument('--midi_folder', type=str)
    parser.add_argument('--hold', type=str, nargs='+', default=['all'])
    parser.add_argument('--exclude', type=str, nargs='+')
    parser.add_argument('--analyze', type=bool, default=False)
    parser.add_argument('--check', type=str, nargs='+')
    parser.add_argument('--length_filter', type=int, default=0)

    arg = parser.parse_args()
    if arg.analyze:
        if arg.midi_folder:
            folder_analyze(arg.midi_folder, arg.length_filter)

        else:
            file_analyze(arg.midi_file)
        
    elif arg.check:
        if arg.midi_folder:
            folder_check_parallel(arg.midi_folder, arg.check, arg.length_filter)

        else:
            file_check(arg.midi_file, arg.check)

    else:
        if arg.midi_folder:
            if arg.exclude:
                folder_exclude(arg.midi_folder, arg.exclude)

            else:
                folder_hold(arg.midi_folder, arg.hold)

        else:
            
            if arg.exclude:
                file_exclude(arg.midi_file, arg.exclude)

            else:
                file_hold(arg.midi_file, arg.hold)
                    