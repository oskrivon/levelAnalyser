from datetime import datetime

def msg_formatter(screening, header):
    msg = header + '\n'
    msg += 'quotation: 24h vol | OI | funding rate | natr' + '\n'
    for i in screening:
        quot = i[0]
        volume = num_formatter(i[1])
        oi = num_formatter(i[2])
        funding_time = i[3]
        natr = round(float(i[4]), 2)

        msg += quot + ': $' + str(volume) + ' | ' + str(oi) + ' | ' + \
               str(funding_time) + ' | ' + str(natr) + '\n'
    return msg


def num_formatter(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'),
                         ['', 'K', 'M', 'B', 'T'][magnitude])


def date_formatter(date_time_str):
    date = datetime.fromisoformat(date_time_str[:-1])
    return date.strftime('%m-%d %H:%M:%S')