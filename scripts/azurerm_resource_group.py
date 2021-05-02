import sys

from utils.utils import get_tf_state_rm_file_path, get_tf_import_state_script_path


def azurerm_resource_group(crf, cde, filter_rg, headers, requests, sub, json, az2tfmess, cldurl):
    # handle resource groups
    """
    :param crf: resource filter
    :param cde: debug
    :param filter_rg: resource group
    :param headers: request headers
    :param requests: requests library object :(
    :param sub: subscription
    :param json: json library object :(
    :param az2tfmess: msg for file
    :param cldurl: cloud domain
    :return:
    """
    isrun = False
    tfp = "azurerm_resource_group"
    if crf in tfp:

        print('# ' + tfp, )

        # fetch all resource groups
        url = "https://" + cldurl + "/subscriptions/" + sub + "/resourceGroups"
        params = {'api-version': '2014-04-01'}
        r = requests.get(url, headers=headers, params=params)
        rgs = r.json()["value"]

        if cde:
            print(json.dumps(rgs, indent=4, separators=(',', ': ')))

        count = len(rgs)
        print(count)
        for j in range(0, count):
            name = rgs[j]["name"]
            rg = name
            loc = rgs[j]["location"]
            id = rgs[j]["id"]

            tf_rm_path = get_tf_state_rm_file_path(resource_name=tfp, resource_group=rg)
            tf_imp_path = get_tf_import_state_script_path(resource_name=tfp, resource_group=rg)
            tf_rm = open(tf_rm_path, 'a')
            tf_imp = open(tf_imp_path, 'a')

            if filter_rg is not None:
                if name.lower() != filter_rg.lower():
                    continue

            rname = name.replace(".", "-")
            if rg[0].isdigit():
                rg = "rg_" + rg

            if rname[0].isdigit():
                rname = "rg_" + rname
            prefix = tfp + "." + rname

            rfilename = prefix + ".tf"
            if isrun:
                fr = sys.stdout
            else:
                fr = open(rfilename, 'w')
            fr.write("")
            fr.write('resource "' + tfp + '" "' + rname + '" {\n')
            fr.write('\t name = "' + name + '"\n')
            fr.write('\t location = "' + loc + '"\n')

            # tags block
            try:
                mtags = rgs[j]["tags"]
            except:
                mtags = "{}"
            tcount = len(mtags) - 1
            if tcount > 1:
                fr.write('tags = { \n')
                # print tcount
                for key in mtags.keys():
                    tval = mtags[key]
                    fr.write(('\t "' + key + '"="' + tval + '"\n'))
                # print(json.dumps(mtags, indent=4, separators=(',', ': ')))
                fr.write('}\n')

            fr.write('}\n')
            if fr is not sys.stdout:
                fr.close()  # close .tf file

            if cde:
                with open(rfilename) as f:
                    print(f.read())

            tf_rm.write('terraform state rm ' + tfp + '.' + rname + '\n')
            tf_imp.write('echo "importing ' + str(j) + ' of ' + str(count - 1) + '"' + '\n')
            tfcomm = 'terraform import ' + tfp + '.' + rname + ' ' + id + '\n'
            tf_imp.write(tfcomm)

        # end for
        tf_rm.close()
        tf_imp.close()
        # end resource group
