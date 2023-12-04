from collections import namedtuple
#
# SRT output
#

Hhmmss_millis = namedtuple(
  'Hhmmss_millis',
  ['hours', 'minutes', 'seconds', 'milliseconds']
)

def convert_seconds_float_into_hms_millis(tfloat=0.0):
    mstart, sstart = divmod(tfloat, 60)
    hstart, mstart = divmod(mstart, 60)
    millisstart = tfloat - ((hstart * 60 * 60) + (mstart * 60) + sstart)
    millisstartint = int(str(millisstart).split(".")[1])
    hstart = int(hstart)
    mstart = int(mstart)
    sstart = int(sstart)

    return Hhmmss_millis(hours=hstart, minutes=mstart, seconds=sstart, milliseconds=millisstartint)

def srt_time_line_from(tstart=0.0, tend=0.1):
    start_time = convert_seconds_float_into_hms_millis(tstart)
    end_time = convert_seconds_float_into_hms_millis(tend)

    # timeString
    timeStr = f'{start_time.hours:02d}:{start_time.minutes:02d}:{start_time.seconds:02d},{start_time.milliseconds:03d}'
    timeStr = timeStr + " --> "
    timeStr = timeStr + f'{end_time.hours:02d}:{end_time.minutes:02d}:{end_time.seconds:02d},{end_time.milliseconds:03d}'
    return timeStr

def output_srt_file(fullOutputFilePath, segments):
    with open(fullOutputFilePath + ".subtitles.srt", mode="wt", encoding='utf-8') as f:
        for segment in segments:
            # the time segment sequential number
            f.write(str(segment["id"]) + "\n")

            # calc srt start time
            timeStr = srt_time_line_from(segment["start"], segment["end"])
            f.write(timeStr + "\n")

            # the actual segement text
            f.write(segment["text"].strip() + "\n")

            # the dividing blank line
            f.write("\n")
