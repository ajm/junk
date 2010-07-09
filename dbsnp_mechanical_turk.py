# quick and dirty script to get allele frequencies
# of SNPs provided on stdin for HapMap-CEU
import urllib2, sys, re


for snpname in sys.stdin :
    snpname = snpname.strip()
    if len(snpname) == 0 :
        continue

    print >> sys.stderr, snpname

    u = urllib2.urlopen('http://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs=%s' % snpname[2:])

    for line in u :

        # find the correct table
        if '<TABLE  id="Diversity">' in line :
            # entries in table
            rows = line.split('</tr>')
            for row in rows :
                # table header
                if '<tr><th bgcolor="silver">ss#</th>' in row :
                    cells = row.split('<th bgcolor="silver">')
                    headings = map(lambda c : c[ : c.find('<')], cells)

                    hindex = headings.index('HWP') + 1
                    vindex = len(headings) - hindex
                    important = headings[ hindex : ]

                # table data
                if row.startswith('<tr valign="bottom">') and ('HapMap-CEU' in row) :
                    cells = row.split('<font size="-1"> ')
                    values = map(lambda c : c[ : c.find('<')], cells)

                    values = values[ -vindex : ]

                    for i in range(len(values)) :
                        if values[i] == '' :
                            values[i] = '0.0'

                    zipped = zip(values,important)
                    zipped.sort()

                    print_values = map(lambda x : "%s %s" % (x[1], x[0]), zipped)

                    toprint = [snpname]
                    other_data = re.findall('<td>\W+(\d+)</td>\ <td>(\w+)</td>', row)
                    if len(other_data) != 1 :
                        print >> sys.stderr, "bad news"
                        sys.exit(-1)

                    toprint += list(other_data[0])

                    print '\t'.join(toprint + print_values)

