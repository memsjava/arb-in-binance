def get_all_triplet(start_coin, data):
    list_key = []
    triplet = []

    for key in data.keys():
        list_key.append(key)

    try:
        for key in list_key:

            if key.endswith(start_coin):

                primary = key
                try:
                    list_key.remove(key)
                    for key_ in list_key:
                        primary_coin = primary.replace(start_coin, '')
                        if key_.endswith(primary_coin):
                            secondary = key_
                            # example ETHBTC
                            secondary_coin = secondary.replace(
                                primary_coin, '')
                            try:
                                for key__ in list_key:
                                    if key__ == secondary_coin + start_coin:
                                        tertiary = key__
                                        triplet.append(
                                            [primary, secondary, tertiary])
                                        list_key.remove(tertiary)
                            except:
                                pass
                            list_key.remove(key_)
                except:
                    pass

    except:
        pass

    return triplet


# this will filter all pairs which current price more than 0.01


def myFilterIsNotBanned(data, triplet):
    res = True
    a1 = data[triplet[0]]
    a2 = data[triplet[1]]
    a3 = data[triplet[2]]

    #  Example 0.01 = price, you can modify this as you want
    if float(a1["b"]) < 0.01 or float(a2["b"]) < 0.01 or float(a3["b"]) < 0.01:
        res = False

    return res


def my_arbitrage(client, data, triplet, capital, start_coin="USDT"):
    res, interest = None, None
    if myFilterIsNotBanned(data, triplet):
        try:
            a1 = data[triplet[0]]
            a2 = data[triplet[1]]
            a3 = data[triplet[2]]
            # print ("start usdt:", capital)
            fee = capital * 0.1 / 100
            step1 = ((capital - fee) / float(a1["b"]))
            # print (triplet[0], " :", step1)
            fee = step1 * 0.1 / 100
            step2 = ((step1 - fee) / float(a2["b"]))
            # print (triplet[1],":", step2)
            fee = step2 * 0.1 / 100
            step3 = ((step2 - fee) * float(a3["a"]))
            # print ("usdt :", step3)

            if (step3 - capital) / capital * 100 > 0.1:
                print("start:", start_coin, capital)
                print(triplet[0], " :", step1, '@', a1["b"])
                print(triplet[1], ":", step2, '@', a2["b"])
                print(start_coin, " :", step3, '@', a3["a"])
                interest = (step3 - capital) / capital * 100
                print("way1: " + str(interest) + "%")
                res = 'way1'

                # print (triplet)
                # print (a1, a2, a3)

            # print ("start usdt:", capital)
            fee = capital * 0.1 / 100
            step1 = ((capital - fee) / float(a3["b"]))
            # print (triplet[2],":", step1)
            fee = step1 * 0.1 / 100
            step2 = ((step1 - fee) * float(a2["a"]))
            # print (triplet[1]," :", step2)
            fee = step2 * 0.1 / 100
            step3 = ((step2 - fee) * float(a1["a"]))
            # print ("usdt :", step3)

            if (step3 - capital) / capital * 100 > 0.1:
                print("start:", start_coin, capital)
                print(triplet[2], ":", step1, '@', a3["b"])
                print(triplet[1], " :", step2, '@', (a2["a"]))
                print(start_coin, " :", step3, '@', a1["a"])
                interest = (step3 - capital) / capital * 100
                print("way2: " + str(interest) + "%")
                res = 'way2'
                # print (triplet)
                # print (a1, a2, a3)
        except:
            pass

    return res, interest
