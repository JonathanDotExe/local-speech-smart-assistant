import datetime

NUMBER_TEXTS = {
            'en': {
                "zero": '00',
                "one": '01',
                "two": '02',
                "three": '03',
                "four": '04',
                "five": '05',
                "six": '06',
                "seven": '07',
                "eight": '08',
                "nine": '09',
                "ten": '10',
                "eleven": '11',
                "twelve": '12',
                "fifteen": '15',
                "twenty": '20',
                "twenty five": '25',
                "twentyfive": '25',
                "thirty": ' 30',
                "thirty five": '35',
                "thirtyfive ": '35',
                "fourty": '40',
                "fourty five": '45',
                "fourtyfive": '45',
                "fifty": '50',
                "fifty five": '55',
                "fiftyfive": '55'
            },
            'de': {
                "null": '00',
                "ein": '01',
                "eins": '01',
                "zwei": '02',
                "drei": '03',
                "vier": '04',
                "fuenf": '05',
                "funf": '05',
                "fünf": '05',
                "sechs": '06',
                "sieben": '07',
                "acht": '08',
                "neun": '09',
                "zehn": '10',
                "elf": '11',
                "zwoelf": '12',
                "zwölf": '12',
                "dreizehn": '13',
                "vierzehn": '14',
                "funfzehn": '15',
                "fuenfzehn": '15',
                "fünfzehn": '15',
                "sechzehn": '16',
                "siebzehn": '17',
                "achtzehn": '18',
                "neunzehn": '19',
                "zwanzig": '20',
                "einundzwanzig": '21',
                "zweiundzwanzig": '22',
                "dreiundzwanzig": '23',
                "fuenfzwanzig": '25',
                "funfzwanzig": '25',
                "fünfundzwanzig": '25',
                "dreissig": '30',
                "fuenfunddreissig": '35',
                "funfunddreissig": '35',
                "fünfunddreissig": '35',
                "vierzig": '40',
                "fuenfundvierzig": '45',
                "fünfundvierzig": '45',
                "funfundvierzig": '45',
                "fünfzig": '50',
                "fuenfzig": '50',
                "funfzig": '50',
                "fünfundfünzig": '55',
                "fuenfundfuenfzig": '55',
                "funfundfunzig": '55'
            }
        }
DATE_TEXTS = {
            'en': {
                "first": '01',
                "second": '02',
                "third": '03',
                "fourth": '04',
                "fifth": '05',
                "sixth": '06',
                "seventh": '07',
                "eighth": '08',
                "ninth": '09',
                "tenth": '10',
                "eleventh": '11',
                "twelfth": '12',
                "thirteenth": '13',
                "fourteenth": '14',
                "fifteenth": '15',
                "sixteenth": '16',
                "seventeenth": '17',
                "eighteenth": '18',
                "nineteenth": '19',
                "twentieth": '20',
                "twenty first": '21',
                "twentyfirst": '21',
                "twenty second": '22',
                "twentysecond": '22',
                "twenty third": '23',
                "twentythird": '23',
                "twenty fourth": '24',
                "twentyfourth": '24',
                "twenty fifth": '25',
                "twentyfifth": '25',
                "twenty sixth": '26',
                "twentysixth": '26',
                "twenty seventh": '27',
                "twentyseventh": '27',
                "twenty eighth": '28',
                "twentyeighth": '28',
                "twenty ninth": '29',
                "twentyninth": '29',
                "thirtieth": '30',
                "thirty first": '31',
                "thirtyfirst": '31'
            },
            'de': {
                "ersten": '01',
                "zweiten": '02',
                "dritten": '03',
                "vierten": '04',
                "fuenften": '05',
                "sechsten": '06',
                "siebten": '07',
                "achten": '08',
                "neunten": '09',
                "zehnten": '10',
                "elften": '11',
                "zwoelften": '12',
                "dreizehnten": '13',
                "vierzehnten": '14',
                "fuenfzehnten": '15',
                "sechzehnten": '16',
                "siebzehnten": '17',
                "achtzehnten": '18',
                "neunzehnten": '19',
                "zwanzigsten": '20',
                "einundzwanzigsten": '21',
                "zweiundzwanzigsten": '22',
                "dreiundzwanzigsten": '23',
                "vierundzwanzigsten": '24',
                "fuenfundzwanzigsten": '25',
                "sechsundzwanzigsten": '26',
                "siebenundzwanzigsten": '27',
                "achtundzwanzigsten": '28',
                "neunundzwanzigsten": '29',
                "dreissigsten": '30',
                "einunddreissigsten": '31'
            }
        }

def parse_time(time1_1: str, time1_2: str, lang: str, isPm: bool = False, addHour: int = 0):
    try:
        time1_1 = time1_1.strip()
        time1_2 = time1_2.strip()

        time1 = ''
        if not time1_1.isdigit():
            time1_1 = get_text_digit(text=time1_1, lang=lang, isPm=isPm, addHour=addHour)
        time1 += time1_1 + ':'
        if not time1_2.isdigit():
            time1_2 = get_text_digit(text=time1_2, lang=lang)
        time1 += time1_2 + ':00'
        return time1
    except:
        return None

def get_text_digit(text: str, lang: str, isPm: bool = False, addHour: int = 0):
    try:
        text = text.strip()

        num_dict = NUMBER_TEXTS[lang]
        is_pm = False
        if lang == 'en':
            if text.endswith('am'):
                text = text.replace('am', '').strip()
            if text.endswith('pm') or isPm:
                is_pm = True
                text = text.replace('pm', '').strip()

        if text in num_dict:
            num = int(num_dict[text]) + addHour
            if num < 10:
                num = '0' + str(num)
            else:
                num = str(num)
            
            if is_pm:
                num = convert_to_pm_time(num)
            return num
        return None
    except:
        return None

# converts a given number to the 24h time
def convert_to_pm_time(num):
    if num == '12':
        num = '00'
    elif num != '00':
        num = str(int(num) + 12)
    return num

def parse_date(text: str, lang: str):
    text = text.strip()

    year = str(datetime.datetime.now().year)
    if lang == 'en':
        months = {
            "january": '01',
            "february": '02',
            "march": '03',
            "april": '04',
            "may": '05',
            "june": '06',
            "july": '07',
            "august": '08',
            "september": '09',
            "october": '10',
            "november": '11',
            "december": '12'
        }
        if ' of ' in text:
            split = text.split(' of ')
        else:
            split = text.split(' ')
        if len(split) >= 2:
            if split[0] in DATE_TEXTS[lang] and split[1] in months:
                day = DATE_TEXTS[lang].get(split[0])
                month = months.get(split[1])
            elif split[1] in DATE_TEXTS[lang] and split[0] in months:
                day = DATE_TEXTS[lang].get(split[1])
                month = months.get(split[0])
            else:
                return None
            datestr = year + '-' + month + '-' + day
            return datetime.datetime.strptime(datestr, '%Y-%m-%d')
        return None
    elif lang == 'de':
        split = text.split(' ')
        if len(split) >= 2:
            day = DATE_TEXTS[lang].get(split[0])
            month = DATE_TEXTS[lang].get(split[1])
            datestr = year + '-' + month + '-' + day
            if not day is None and not month is None:
                return datetime.datetime.strptime(datestr, '%Y-%m-%d')
    return None