#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import libraries

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


# In[2]:


# import data as padas dataframes

sales_report = pd.read_csv("C:/Users/anton/Documents/Python Project/Data/Amazon Sale Report.csv", low_memory = False)
may_sales = pd.read_csv("C:/Users/anton/Documents/Python Project/Data/May-2022.csv", low_memory = False)
other_sales_report = pd.read_csv("C:/Users/anton/Documents/Python Project/Data/Sale Report.csv", low_memory = False)


# # Explore Data

# In[3]:




sales_report.info()

# there are some columns that are missing a lot of values, will need to drop them - unnamed, fulfilled-by
# there are 23 columns
# only 3 of them are numericals - Qty, Amount and Ship-post-code

## will need to change Date to a date datatype


# In[4]:


sales_report.describe()

# confirmed from the above there are only 3 numerical columns
# Amount and Ship-postal-code are missing data


# In[5]:


sales_report.head()


# In[6]:


sales_report.shape


# In[7]:


sales_report.columns


# In[8]:


# Check May Sales Report for columns we can merge on
may_sales.head()


# In[9]:


may_sales.info()

# can merge on Sku but need to rename


# In[10]:


# rename Sku to SKU for easier joining with sales_report dataframe
may_sales = may_sales.rename(columns = {"Sku" : "SKU"})


# In[11]:


merged_test1 = pd.merge(sales_report, may_sales, on = "SKU", how = "inner")

if merged_test1.empty:
    print ("No common SKUs found")
else:
    print("Common SKUs found")
    
# no common SKUs, try another dataset to merge on


# In[12]:


other_sales_report.head()
other_sales_report.info()


# In[13]:


# rename Sku to SKU for easier joining with sales_report dataframe
other_sales_report = other_sales_report.rename(columns = {"SKU Code" : "SKU"})


# In[14]:


merged_test2 = pd.merge(sales_report, other_sales_report, on = "SKU", how = "inner")

if merged_test2.empty:
    print ("No common SKUs found")
else:
    print("Common SKUs found")
    
# Can work with this data set


# In[15]:


merged_test2.info()
# need to clean up names in other_sales_report


# # Data Cleaning - Sales Report

# In[16]:


sales_report.nunique()

# there are 120,378 unique order IDs vs 128,975 rows in the index. Need to drop duplicates


# In[17]:


# drop rows with the same order ID

sales_report.drop_duplicates(subset = "Order ID", inplace = True)


# In[18]:


# explore null values

print((sales_report.isnull()).sum())


# In[19]:


# address the columns with lots of missing data

# if couriers status is missing, change to "unkown"
sales_report["Courier Status"].fillna("unkown", inplace = True)

# if promotion-id is missing, assume there was no promotion
sales_report["promotion-ids"].fillna("no promotion", inplace = True)   

# if fulfilled-by is missing, change to "unkown"
sales_report["fulfilled-by"].fillna("unknown", inplace = True)

# if no currency data, replace with INR
sales_report["currency"].fillna("INR", inplace = True)


# In[20]:


# drop the unnamed: 22 column. Unknown column offers no insight

sales_report.drop(columns = ["Unnamed: 22"], inplace = True)


# In[21]:


# confirm that that the 28 entries with missing ship- data are the same rows

sales_report[sales_report["ship-city"].isnull()]


# In[22]:


# confirmed. Can now drop those 28 rows
sales_report.dropna(subset = "ship-city", inplace = True)


# In[23]:


# delete rows with zero amount and no promotion id

drop_if = (sales_report["Amount"]) == 0 & (sales_report["promotion-ids"] == "no promotion")
                                        
sales_report = sales_report.drop(sales_report[drop_if].index)                 


# In[24]:


# check again
sales_report.info()

# we now have data about orders with no duplicates and no missing values


# In[25]:


# change to the date column into datetime type
sales_report["Date"] = pd.to_datetime(sales_report["Date"], format = "%m-%d-%y")


# In[26]:


# set the index column to be the index
sales_report.set_index("index", inplace = True)


# In[27]:


# rename columns

rename_array = {"ship-service-level" : "Service Level", "Amount" : "Amount in INR", "ship-city":"City", "ship-state":"State", "ship-postal-code":"Post Code", "ship-country":"country", "B2B":"Customer Type"}

sales_report.rename (columns = rename_array, inplace = True)
sales_report.head()


# In[28]:


# change customer type column to Business (True) or Consumer (False)

sales_report["Customer Type"].replace([True, False], ["business", "consumer"], inplace = True)

sales_report["Customer Type"]


# In[29]:


# Country is India, check how many unique states there are
print(sales_report["State"].unique())

# need to clean up duplicates - e.g "Goa" vs "GOA"


# In[30]:





# In[31]:


# Noticed that Quantity for some orders is zero - check this
print(sales_report["Qty"].unique())


# In[32]:


# Add a column with GBP as the currency instead of INR to make it more relatable

sales_report["Amount in GBP"] = sales_report["Amount in INR"] * 0.0099


# # Data Cleaning - Other Sales Report

# In[33]:


other_sales_report.nunique()

# 9271 entries vs 9170 with SKUs


# In[34]:


other_sales_report = other_sales_report.dropna(subset = ["SKU"])
other_sales_report.info()


# In[35]:


# rename columns with common names
renames = {"Category": "Category_Other", "Size": "Size_Other"}
other_sales_report = other_sales_report.rename(columns = renames)

# set the index column to be the index
other_sales_report.set_index("index", inplace = True)


# In[36]:


other_sales_report.info()


# # Data Analysis - Sales Report

# In[37]:


"""
Write a formula that takes a column name as an input and checks
1) How many unique values there are in that column
2) How many times does that unique value appear in the column
3) Plots a barchart to visualize the distribution

"""

def summarize(column):
    # count how often each unique value appears
    counts = sales_report[column].value_counts()
    
    # plot the unique values
    
    sns.barplot(x = counts.index, y = counts.values)
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.xticks (rotation=45, ha = "right", rotation_mode = "anchor") #adjust the labels so they dont overlap
    plt.show()
    print("\n")
    print (f"Number of unique values: {len(counts)}")
    print (f"Frequency of each unique value: {counts}")
    


# In[38]:


summarize("Status")


# In[39]:


# Write a loop function to the above for every non-numeric column with less than 15 unique values

def summarize_all_columns (df):
    for column in df.columns:
        if df[column].dtype != "float64" and df[column].dtype != "int64":
            unique_values = df[column].nunique()
            if unique_values <= 15:
                print("---Column:",column)
                summarize(column)
                print("\n")


# In[40]:


# Output

summarize_all_columns(sales_report)

# >72k orderes are shipped
# >26k have been delivered


# In[41]:


# An exception to the above rule for states

summarize("State")


# In[42]:


# What is the average spend by order?

sales_report["Amount in GBP"].describe()

# The average order is £6.6
# The max order is £54.4
# The min order is £1.9 


# In[43]:


sales_report.sort_values("Amount in GBP", ascending = True)


# In[44]:


# Is there any difference in average spend by service level?

grouped_by_service = sales_report.groupby("Service Level")["Amount in GBP"].mean()

print (grouped_by_service)

# there is no meaningful difference in the average spend byt service level


# In[45]:


# is there any difference in average spend by size?

grouped_by_size = sales_report.groupby("Size")["Amount in GBP"].mean()

print (grouped_by_size)

sns.barplot(x=grouped_by_size.index, y=grouped_by_size.values)
plt.xlabel = ("Size")
plt.ylabel = ("Avg Amount in GBP")


# In[46]:


# Is there a difference in average spend by state?

grouped_by_state = sales_report.groupby("State")["Amount in GBP"].mean()


print (f"The highest average spend is in : {grouped_by_state.idxmax()} at £ {round(grouped_by_state.max(),2)}")
print (f"The lowest average spend is in : {grouped_by_state.idxmin()} at £ {round(grouped_by_state.min(),2)}")



sns.barplot(x=grouped_by_state.values, y=grouped_by_state.index, orient = "h")
plt.xlabel = ("State")
plt.ylabel = ("Avg Amount in GBP")
plt.show()


# In[56]:


# any spending patterns by date?

grouped_by_date = sales_report.groupby("Date")["Amount in GBP"].sum()

sns.scatterplot (x= grouped_by_date.index, y = grouped_by_date.values)
plt.xticks (rotation=45, ha = "right", rotation_mode = "anchor") #adjust the labels so they dont overlap
plt.show()


# # Data Analysis on Merged DataFrame

# In[48]:


merged_sales = pd.merge(sales_report, other_sales_report, on = "SKU", how = "inner")


# In[49]:


merged_sales.info()


# In[50]:


merged_sales.head()


# In[51]:


counts = merged_sales["Color"].value_counts()
    
# plot the unique values
    
sns.barplot(x = counts.index, y = counts.values)

plt.xticks (rotation=45, ha = "right", rotation_mode = "anchor") #adjust the labels so they dont overlap
plt.show()
print("\n")
print (f"Number of unique values: {len(counts)}")
print (f"Frequency of each unique value: {counts}")
    


# In[64]:


# Standardizing the data
merged_sales.loc[merged_sales['Color'].isin(['Light Green','Turquoise Green','Sea Green','TEAL GREEN','Teal Green ', 'Dark Green', 'MINT GREEN', 'MINT','LIME GREEN', 'Olive','Teal Green', 'Olive Green']),'Color'] = 'Green'
merged_sales.loc[merged_sales['Color'].isin(['Navy Blue','NAVY']),'Color'] = 'Navy'
merged_sales.loc[merged_sales['Color'].isin(["Turquoise Blue","Teal Blue ", "Sky Blue", "Powder Blue","Light Blue", "Dark Blue "]),'Color'] = 'Blue'
merged_sales.loc[merged_sales['Color'].isin(["LIGHT YELLOW","LEMON", "LEMON ", "Lemon Yellow", "Gold"]),'Color'] = 'Yellow'
merged_sales.loc[merged_sales['Color'].isin(['CORAL ORANGE']),'Color'] = 'Orange'


merged_sales["Color"] = merged_sales["Color"].apply(lambda x: x.title()) 

counts = merged_sales["Color"].value_counts()
    
# plot the unique values again
    
sns.barplot(x = counts.index, y = counts.values)

plt.xticks (rotation=45, ha = "right", rotation_mode = "anchor") #adjust the labels so they dont overlap
plt.show()
print("\n")
print (f"Number of unique values: {len(counts)}")
print (f"Frequency of each unique value: {counts}")


# In[ ]:




