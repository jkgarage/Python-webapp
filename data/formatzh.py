import re
def process_type1(filename):
  f = open(filename, 'r')
  newfile = open('out.txt', 'w')
  for line in f:
    line = line.strip()
    if line == '#stop.here.': break
    if len(line) == 0 or line[0] == '#': continue

    parts = re.split('[()-]+', line)
    parts = [v.strip() for v in parts if v.strip() != '']
    print parts
    newline = ''
    if len(parts) == 3:
      newline = ('name,%s,%s,%s\n' % (parts[1], parts[2], parts[0]))
      newfile.write(newline)
    print newline
  f.close()
  newfile.close()


def process_type2(filename):
  f = open(filename, 'r')
  newfile = open('out.txt', 'w')
  for line in f:
    line = line.strip()
    if line == '#stop.here.': break
    if len(line) == 0 or line[0] == '#': continue
    
    parts = re.split('[\[\]/]+', line)
    parts = [v.strip() for v in parts if v.strip() != '']
    print parts
    newline = ''
    if len(parts) == 3:
      newline = ('name,%s,%s,%s\n' % (parts[0], parts[1], parts[2]))
      newfile.write(newline)
    print newline
  f.close()
  newfile.close()


def process_cdict(filename):
  f = open(filename, 'r')
  newfile = open('out.txt', 'w')
  for line in f:
    line = line.strip()
    if line == '#stop.here.': break
    if len(line) == 0 or line[0] == '#': continue
    
    parts = re.split('[\[\]\/]+', line, maxsplit=3)
    parts = [v.strip() for v in parts if v.strip() != '']
    #print parts
    newline = ''
    if len(parts) == 3:
      arr = re.split(' +', parts[0])
      simplifiedzh = arr[1]
      newline = ('cdict,%s,%s,%s\n' % (simplifiedzh, parts[1], parts[2]))
      newfile.write(newline)
    #print newline
  f.close()
  newfile.close()


process_cdict('cedict_ts.mini.u8')