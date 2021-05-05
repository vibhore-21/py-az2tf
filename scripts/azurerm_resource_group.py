import sys

from utils.utils import get_tf_state_rm_file_path, get_tf_import_state_script_path, \
    get_tf_config_file_path, get_tf_compatible_rg


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
    tf_code = "001"
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
            if filter_rg is not None:
                if rg.lower() != filter_rg.lower():
                    continue

            tf_rg = get_tf_compatible_rg(name)
            tf_name = tf_rg
            rfilename = get_tf_config_file_path(tfp, tf_name, 'rg')
            if isrun:
                fr = sys.stdout
            else:
                fr = open(rfilename, 'a')
            fr.write("")
            fr.write('resource "' + tfp + '" "' + tf_name + '" {\n')
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

            # write state rm file
            tf_rm_path = get_tf_state_rm_file_path(resource_type=tfp, prefix=tf_code, resource_group=tf_rg)
            tf_rm = open(tf_rm_path, 'a')
            tf_rm.write('terraform state rm ' + tfp + '.' + tf_name + '\n')
            tf_rm.close()

            # write state imp file
            tf_imp_path = get_tf_import_state_script_path(resource_type=tfp, prefix=tf_code, resource_group=tf_rg)
            tf_imp = open(tf_imp_path, 'a')
            tf_imp.write('echo "importing ' + str(j) + ' of ' + str(count - 1) + '"' + '\n')
            tfcomm = 'terraform import ' + tfp + '.' + tf_name + ' ' + id + '\n'
            tf_imp.write(tfcomm)
            tf_imp.close()

        # end for
        # end resource group
