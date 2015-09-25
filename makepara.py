s = 14

a = [i.strip().split(" ") for i in open("cbs.txt").readlines()]

ordering = [i for i in a[0] if i != 'f']


for num, thing in enumerate(a):
    f = open("paras/SyntCat_c{}.para".format(num + 1), "w")
    f.write("""#onsets""")
    t = -s
    itemsused = []
    for cat in thing:
        t += s
        if cat != "f":
        
            f.write(str(t/2) + " " + str(ordering.index(cat) + 1) + "\n")
        else:
            f.write("\n")

    f.write("""#names\n""")
    f.write(" ".join(ordering) + "\n")

    f.write("""\n#durations\n""")
    f.write(" ".join([str(s/2)]*18))

    f.close()
    
