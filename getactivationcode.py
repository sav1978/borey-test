import urllib.request

URL = "http://10.1.31.23:8080/activation/remote/?delivery_uid=ef099abf-af51-4780-aa69-67bd064c0d3c&device_uid="

def get_act_code(id_sd_card):
   url = URL + id_sd_card
   response = urllib.request.urlopen(url)
   activation_code = response.read()
   return activation_code

print(get_act_code("02544d5341303447163a8a0ce300f423"))