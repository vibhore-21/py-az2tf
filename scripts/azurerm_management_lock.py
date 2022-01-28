import uuid

from utils.utils import get_tf_config_file_path, get_logger, get_tf_compatible_name

logger = get_logger(logger_name='management_lock')


def azurerm_management_lock(crf, cde, crg, headers, requests, sub, json, az2tfmess, cldurl):
    # management locks

    resource_type = "azurerm_management_lock"
    azr = ""
    if crf in resource_type:
        # REST
        # # print "REST VNets"
        url = "https://" + cldurl + "/subscriptions/" + sub + "/providers/Microsoft.Authorization/locks"
        params = {'api-version': '2017-04-01'}
        r = requests.get(url, headers=headers, params=params)
        azr = r.json()["value"]

        tfrmf = "002-" + resource_type + "-staterm.sh"
        tfimf = "002-" + resource_type + "-stateimp.sh"
        tfrm = open(tfrmf, 'a')
        tfim = open(tfimf, 'a')
        print("# " + resource_type, )
        count = len(azr)
        print(count)
        for j in range(0, count):

            name = azr[j]["name"]

            # name=name.encode('utf-8', 'ignore')

            # loc=azr[j]["location"]
            id = azr[j]["id"]
            rg_orginal = id.split("/")[4]
            if crg is not None:  # filter by resource_group
                if rg_orginal.lower() != crg.lower():
                    continue

            tf_rg = rg_orginal.replace(".", "-").lower()
            if tf_rg[0].isdigit():
                tf_rg = "rg_" + tf_rg

            level = azr[j]["properties"]["level"]

            # get scope and tf scope name
            scope1 = id.split("/Microsoft.Authorization")[0].rstrip("providers")
            scope = scope1.rstrip("/")
            sc = len(scope.split("/"))
            logger.debug("for management lock name: {}, value of scope is {}".format(name, scope))
            tf_scope = scope.split("/")[sc - 1].replace(" ", "-").lower()  # tf_scope : terraform scope name ?
            tf_scope = tf_scope.replace(".", "-")
            # scope=scope.encode('utf-8', 'ignore')
            # tf_scope=tf_scope.encode('utf-8', 'ignore')

            tf_name = get_tf_compatible_name(name)

            if cde:
                print(json.dumps(azr[j], indent=4, separators=(',', ': ')))

            # compute tf complete name & handle scope
            try:
                tf_resource_name = tf_rg + '__' + tf_name + '__' + tf_scope
            except UnicodeDecodeError:
                print('Problem with the scope name: ' + scope)
                print('Please rename this item in the Azure Portal')
                tf_scope = str(uuid.uuid4())
                # tf_scope=tf_scope.encode('utf-8', 'ignore')
                tf_resource_name = tf_rg + '__' + tf_name + '__' + tf_scope

            # prefix=tfp+"."+rg+'__'+rname

            rfilename = get_tf_config_file_path(resource_type, tf_rg, tf_name, tf_scope)
            fr = open(rfilename, 'w')
            fr.write('resource ' + resource_type + ' "' + tf_resource_name + '" {\n')
            fr.write('\t name = "' + name + '"\n')
            fr.write('\t lock_level = "' + level + '"\n')

            try:
                notes = azr[j]["properties"]["notes"]
                # notes=notes.encode('utf-8', 'ignore')
                notes = notes.replace('"', '\\"')
                fr.write('\t notes = "' + notes + '"\n')
            except KeyError:
                pass
            fr.write('\t scope = "' + scope + '"\n')
            # tags block

            # tags block
            try:
                mtags = azr[j]["tags"]
                fr.write('tags = { \n')
                for key in mtags.keys():
                    tval = mtags[key]
                    # fr.write(('\t "' + key + '"="' + tval + '"\n'))
                    fr.write(('\t "' + key + '"="' + tval + '"\n'))
                fr.write('}\n')
            except KeyError:
                pass

            # try:
            #    mtags=azr[j]["tags"]
            # except:
            #    mtags="{}"
            # tcount=len(mtags)-1
            # if tcount > 1 :
            #    fr.write('tags = { \n')
            #    print tcount
            #    for key in mtags.keys():
            #        tval=mtags[key]
            #        fr.write(('\t "' + key + '"="' + tval + '"\n'))
            #    #print(json.dumps(mtags, indent=4, separators=(',', ': ')))
            #    fr.write('}\n')

            fr.write('}\n')
            fr.close()  # close .tf file

            if cde:
                with open(rfilename) as f:
                    print(f.read())

            tfrm.write('terraform state rm ' + resource_type + '.' + tf_resource_name + '\n')

            tfcomm = 'terraform import ' + resource_type + '.' + tf_resource_name + ' "' + id + '"\n'
            tfim.write('echo "importing ' + str(j) + ' of ' + str(count - 1) + '"' + '\n')
            # tfcomm=tfcomm.encode('utf-8', 'ignore')
            tfim.write(tfcomm)

            # end for
        tfrm.close()
        tfim.close()
        # end management locks
