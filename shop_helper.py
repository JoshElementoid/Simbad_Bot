# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 15:13:59 2021

@author: Josh
"""


import pandas as pd
import numpy as np

class shop (object):

    def __init__ (self, money_path, items_path):
        """
        The shop class for the Discord bot. Needs 2 things to initialize: 
           -  the path for the shop item prices csv, and
           -  the path for the member balance/inventory csv

        """    
        self.money_path = money_path
        self.items_path = items_path
        
        self.bal_df = pd.read_csv(money_path)
        self.shop_df = pd.read_csv(items_path)
        
        # print("Dataframes loaded") 
        return
    
    
    def name_init (self):
        # Writes the column name row for the csv file
        
        item_columns = list(self.shop_df['item'])
        col_names = "member_id,balance,"
        col_names += ",".join(item_columns)
        
        with open(self.money_path, "w") as f:
            f.write(col_names)
            f.close()
        
        self.bal_df = pd.read_csv(self.money_path)
        
        return
        
    
    def member_init (self, member_id):
        # Initializes a row for a particular member
        
        item_columns = list(self.shop_df['item'])   
        num_items = len(item_columns)
        
        s2w = "\n{},{}".format(member_id,0)
        s2w += num_items*",0"
        
        with open(self.money_path, "a") as f:
            f.write(s2w)
            f.close()
        
        self.bal_df = pd.read_csv(self.money_path)
        
        return
        
        
    def change_balance (self, member_id, amount): 
        # Change the balance of member_id by amount
        
        amount = float(amount)
        member_df = self.bal_df["member_id"] == member_id
        self.bal_df.loc[member_df, "balance"] += amount
        
        self.rewrite_bal_csv()
        
        return
    
    
    def show_inv (self, member_id):
        
        """
        Given a member_id, returns a zip in the format of:
        [(item, amount), (item, amount), etc..]
            
        Example:
        [("balance", 500), ("apple", 1), ("orange", 5)]
        
        """
        
        # Gets the quantity of every shop item that the user has:
        df = self.bal_df
        df = df.loc[df["member_id"] == member_id, "balance":]
        
        col_labels = list(df.columns)   # column names
        quan_arr = np.asarray(df, dtype="uint32")[0]
         
        zipped = zip(col_labels, quan_arr)

        return zipped
    
        
    def buy (self, member_id, item_name, quantity=1):
        # Find the dfs for the member and the item
        member_df = self.bal_df["member_id"] == member_id
        item_df = self.shop_df["item"] == item_name.lower()
   
        # Member balance:
        member_balance = self.bal_df.loc[member_df, "balance"]
        
        # Item information:
        item_id = self.shop_df.loc[item_df, "id"]
        item_price = self.shop_df.loc[item_df, "price"]
        item_quan = self.shop_df.loc[item_df, "quantity"]
    
        total_price = quantity * item_price.item()
        
        if not any(item_df):
            msg = "No such item"

            return msg
        
        if total_price > member_balance.item():
            msg = "You do not have enough Simbits"

            return msg
        
        if item_quan.item() < 1:
            msg = "Item is currently out of stock. Sorry!"
            
            return msg
        
        # Remove 
        
        # Deducting money from user balance:
        self.change_balance (member_id, -total_price)
        
        # Adding item to inventory:
        self.bal_df.loc[member_df, item_name.lower()] += quantity
        
        # Returns a message of the transaction:
        msg = "You succesfully purchased {} {} for {} Simbits\n".format(
            quantity, item_name.title(), total_price)

        msg += "New balance: {}".format(
            self.bal_df.loc[member_df, "balance"].item())
        
        
        self.rewrite_bal_csv()
        
        return msg
    
    
    # Methods for updating the .csv file when the df is changed:
    
    def rewrite_bal_csv (self):
        # Writes the member balance df to csv
        self.bal_df.to_csv(self.money_path, encoding="utf-8")
        
        return
    

    def rewrite_item_csv (self):
        self.shop_df.to_csv(self.items_path, encoding="utf-8")

        return 


#%%

if __name__ == "__main__":
    
    me_id = 117431457202438148
    other_id = 666454811884912640
    
    path1 = "C:\\Users\\Josh\\Desktop\\Misc\\Simbad\\static\\cash_money.csv"
    path2 = "C:\\Users\\Josh\\Desktop\\Misc\\Simbad\\config\\shop_items.csv"
    path3 = "C:\\Users\\Josh\\Desktop\\Misc\\Simbad\\static\\inventory.csv"
    
    market = shop(path1, path2)
    
    market.name_init()
    
    #%%
    market.member_init(me_id)
    market.member_init(other_id)
    market.change_balance(me_id, 50000)
    
    #%% Buying
    
    trans_msg = market.buy(me_id, "ice cream")
    trans_msg = market.buy(me_id, "orange", 5)
        
    # print(trans_msg)
    
    #%%
    inv = market.show_inv(me_id)
    
    print(list(inv))











