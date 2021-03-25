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
    
    
    def shop_prices (self):
        """
        Returns an array of tuples in the format
        [ [item, price, quantity], [item, price quantity], etc.]
        
        Example:
        [['apple', 10, 5], ['banana', 20, 6]]
        
        """
        
        return self.shop_df.to_numpy()
    
    
    def member_balance(self, member_id):
        member_df = self.bal_df["member_id"] == member_id

        # Member balance:
        member_balance = self.bal_df.loc[member_df, "balance"]
        
        return member_balance.item()
        
        
    def change_balance (self, member_id, amount): 
        # Change the balance of member_id by amount
        
        amount = float(amount)
        member_df = self.bal_df["member_id"] == member_id
        self.bal_df.loc[member_df, "balance"] += amount
        
        self.rewrite_bal_csv()
        
        return
    
    
    def show_inv (self, member_id):
        
        """
        Returns a string representation of a member's inventory
        
        """
        
        # Gets the quantity of every shop item that the user has:
        df = self.bal_df
        df = df.loc[df["member_id"] == member_id, "balance":].to_numpy()
        df = df.reshape((df.shape[1]))
    
        item_names = self.bal_df.columns.to_numpy()[1:]
        
        together = np.stack((item_names, df), axis=1)
        
        template = "{0:15}│{1:10}\n"
        
        inv_str = "Item"+11*" "+"│" 
        inv_str += 4*" "+"Amount\n" 
        inv_str += 26*"—"+"\n"

        for x in together:
            inv_str += template.format(*x)
    
    
        return inv_str
    
        
    def buy (self, member_id, item_name, quantity=1):
        
        if quantity <= 0:
            msg = "What the fuck?"
            
            return msg
        
        # Find the dfs for the member and the item
        member_df = self.bal_df["member_id"] == member_id
        item_df = self.shop_df["item"] == item_name.lower()
    
   
        # Member balance:
        member_balance = self.bal_df.loc[member_df, "balance"]
        
        # Item information:
        item_price = self.shop_df.loc[item_df, "price"]
        item_quan = self.shop_df.loc[item_df, "quantity"]
    
        total_price = quantity * item_price.item()
        
        if not any(item_df):
            msg = "No such item"

            return msg
        
        if float(total_price) > member_balance.item():
            msg = "You do not have enough Simbits"

            return msg
        
        if quantity > item_quan.item():
            msg = "Not enough items left in stock. Sorry!"
            
            return msg
        
        # Remove quantity from shop item:
        self.shop_df.loc[item_df, "quantity"] -= quantity
        
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
        self.rewrite_item_csv()
        
        return msg
    
    
    def donate (self, from_id, to_id, amount):
        """
        Give amount of your money to someone else
    
        """
        
        if amount <= 0:
            msg = "What the fuck?"
            
            return msg
        
        from_df = self.bal_df["member_id"] == from_id
        from_bal = self.bal_df.loc[from_df, "balance"].item()
        
        if from_bal < amount:
            msg = "You don't have enough money!"
        
        else:
            self.change_balance(from_id, -amount)
            self.change_balance(to_id, +amount)
            
            msg = "You gave {} to <@{}>".format(amount, to_id)
        
        return msg
        
    
    def remove_item (self, member_id, item, quantity):
        """
        Removes quantity amount of item from member_id's inventory
        
        
        """
        item = item.lower()
        
        member_df = self.bal_df["member_id"] == member_id 
        
        # The amount of the item the member currently have:
        item_quan = self.bal_df.loc[member_df, item].item()
        
        if item_quan - quantity < 0:
            msg = "Failed. The person has {} {}, but you are trying to remove {} {}"
            msg = msg.format(item_quan, item.title(), quantity, item.title())
        
            return msg
        
        self.bal_df.loc[member_df, item] -= quantity
        self.rewrite_bal_csv()
        
        msg = "Successfully removed {} {}. {} {} remaining"
        msg = msg.format(quantity, item.title(), item_quan-quantity, item.title())
        
        return msg
        
        
    # Methods for updating the .csv file when the df is changed:
    
    def rewrite_bal_csv (self):
        # Writes the member balance df to csv
        self.bal_df.to_csv(self.money_path, encoding="utf-8", index=False)
        
        return
    

    def rewrite_item_csv (self):
        self.shop_df.to_csv(self.items_path, encoding="utf-8", index=False)

        return 
    
    
    def reload (self):
        self.bal_df = pd.read_csv(self.money_path)
        self.shop_df = pd.read_csv(self.items_path) 
        
        
    def shop_show (self):
        """
        I hate string processing
        """
        
        template = "{0:15}│{1:10}│{2:10}\n"
        shop_str = ""
        
        together = self.shop_df.to_numpy()
        
        # Hardcoding the header row because I suck at string formatting...
        header = "Item"+11*" "+"│" 
        header += 6*" "+"Cost"+"│"
        header += "     Stock" 

        shop_str += header + "\n"
        shop_str += 37*"—"+"\n"
        
        for x in together:
            shop_str += template.format(*x)
        
        return shop_str

#%%

if __name__ == "__main__":
    
    me_id = 117431457202438148
    other_id = 666454811884912640
    
    path1 = "C:\\Users\\Josh\\Desktop\\Misc\\Simbad\\static\\cash_money.csv"
    path2 = "C:\\Users\\Josh\\Desktop\\Misc\\Simbad\\config\\shop_items.csv"
    
    market = shop(path1, path2)
    # foo = market.shop_show()
    
    member_inv = market.show_inv(me_id)

    print(member_inv)



















