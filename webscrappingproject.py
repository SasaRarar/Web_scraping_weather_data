from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import numpy as np
import h5py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



# change to your folder path
home_dir = "path" # change path

websites_list = []
with open(home_dir+"DQDW_weatherdata_web_pages.csv") as file:
    for line in file:
        websites_list.append(line)

website_1 = websites_list[0]       
website_2 = websites_list[1]
website_3 = websites_list[2]

# run the browser in headless mode
options = webdriver.FirefoxOptions()
options.add_argument("--headless=new")


driver = webdriver.Firefox(options=options)
driver.get(website_1)
elem = driver.find_elements(By.ID, "wetklitab")
bloc1=elem[0].text
bloc2=elem[1].text
#copy weatherdata into a list
list_bloc1 = bloc1.split()
list_bloc2 = bloc2.split()


date = list_bloc1[3]
date = date.split(".")
date = np.array([int(date[0]), int(date[1]), int(date[2])])
#we always take the temperature at noon
temperature_fra = list_bloc2[8]

temperature_fra = [int(temperature_fra)]

print(temperature_fra)



driver.get(website_2)
#cookie window has to be closed
try:
    cookie_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "ccc-reject-settings")))
    cookie_button.click()
except:
    print("cookie button could not be closed")
elem = driver.find_element(By.CLASS_NAME, "link-forecast")
driver.execute_script("arguments[0].scrollIntoView(true);", elem)
elem.click()
elem = driver.find_element(By.CLASS_NAME, "forecast-table")
forecasttable = elem.text
list_forecasttable = forecasttable.split()


x = list_forecasttable.index("12:00")

temperature_lhr_position = x+39
temperature_lhr = list_forecasttable[temperature_lhr_position]

temperature_lhr_int = int(temperature_lhr.replace("°",""))

temperature_lhr = [temperature_lhr_int]

#print(temperature_lhr)



driver.get(website_3)
today_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "_cardContent_qjy2j_145")))
today_button.click()

elem = driver.find_element(By.CLASS_NAME, "_tableContainer_mh5eb_131")
weather_table_arn = elem.text
list_weather_table_arn = weather_table_arn.split()

y = list_weather_table_arn.index("12")
temperature_arn_position = y+1
temperature_arn = list_weather_table_arn[temperature_arn_position]
temperature_arn_cleaned = temperature_arn.replace("°","").strip()
temperature_arn_cleaned = temperature_arn_cleaned.replace("−", "-")  # Unicode-Minuszeichen ersetzen
temperature_arn_int = int(temperature_arn_cleaned)

temperature_arn = [temperature_arn_int]

print(temperature_arn)



date = np.array([date])

date_scalar = f"{date[0][2]}-{date[0][1]:02d}-{date[0][0]:02d}" 
print(date)




# Combining data in a single dataset
data = np.array([(date_scalar, temperature_fra[0], temperature_lhr[0], temperature_arn[0])], dtype=[("date", "S10"), ("temp_fra", "f4"), ("temp_lhr", "f4"), ("temp_arn", "f4") ])

# save all data in a single data set
with h5py.File(home_dir+'weatherdata.hdf5', 'a') as file:
    if "weather_data" not in file:
        # create new dataset 
        dataset = file.create_dataset("weather_data", data=data, maxshape=(None,), chunks=True)
    else:
        # extent data
        existing_data = file["weather_data"][:]
        combined_data = np.concatenate((existing_data, data))
        del file["weather_data"]
        dataset = file.create_dataset("weather_data", data=combined_data, maxshape=(None,), chunks=True)




file.close()
driver.quit()







