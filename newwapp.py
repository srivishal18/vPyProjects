import tkinter as tk
from tkinter import *
from tkinter import Entry
from tkinter import messagebox
import mysql.connector

vidb = mysql.connector.connect(host="localhost", user="root", passwd="Vishalpy$99", database="VishyyBucks")

mycursor = vidb.cursor()

root = Tk()

root.title("Stealth Billing Software")

canvas = tk.Canvas(root, width=900, height=720)
canvas.grid(columnspan=3, rowspan=18)


# Functions


def add_tables():
    add_window = Toplevel()
    add_window.title("Add Tables")
    canvas = tk.Canvas(add_window, width=480, height=270)
    canvas.grid(columnspan=3, rowspan=9)
    Label(add_window, text="Please Enter your product name").grid(row=0, column=1)
    global vientry1, vientry2, vientry3, vientry4, vientry5, vientry6, vientry7
    vientry1 = IntVar()
    vientry2 = IntVar()
    vientry3 = StringVar()
    vientry4 = StringVar()
    vientry5 = IntVar()
    vientry6 = IntVar()
    Entry(add_window, textvariable=vientry1).grid(row=1, column=1)
    Entry(add_window, textvariable=vientry2).grid(row=2, column=1)
    Entry(add_window, textvariable=vientry3).grid(row=3, column=1)
    Entry(add_window, textvariable=vientry4).grid(row=4, column=1)
    Entry(add_window, textvariable=vientry5).grid(row=5, column=1)
    Entry(add_window, textvariable=vientry6).grid(row=6, column=1)
    Button(add_window, text="Proceed", command=store_values_add).grid(row=7, column=1)
    Button(add_window, text="Done", command=add_window.destroy).grid(row=8, column=1)


def store_values_add():
    orderid = vientry1.get()
    customerid = vientry2.get()
    customername = vientry3.get()
    productname = vientry4.get()
    productprice = vientry5.get()
    productquantity = vientry6.get()
    totalprice = productquantity * productprice

    addvalues = "INSERT INTO orders values(%s,%s,%s,%s,%s,%s,%s)"
    addvalues_list = []
    list1 = [orderid, customerid, customername, productname, productprice, productquantity, totalprice]
    for i in list1:
        addvalues_list.append(i)
    addvalues_tuple = [tuple(addvalues_list)]
    mycursor.executemany(addvalues, addvalues_tuple)
    vidb.commit()


def edit_tables_button():
    view_window = Toplevel()
    viewcanvas = tk.Canvas(view_window, width=480, height=270)
    viewcanvas.grid(columnspan=3, rowspan=7)
    view_window.title("Edit Tables")
    global viview1, viview2, viview3
    viview1 = StringVar()
    viview2 = StringVar()
    viview3 = IntVar()
    Label(view_window, text="Please Enter a suitable table name to edit from below").grid(row=0, column=1)
    Label(view_window, text="customername, customerid, productname, productprice, productquantity").grid(row=1,
                                                                                                         column=1)
    Entry(view_window, textvariable=viview1).grid(column=1, row=2)
    Entry(view_window, textvariable=viview2).grid(column=1, row=3)
    Entry(view_window, textvariable=viview3).grid(column=1, row=4)
    Button(view_window, text="Enter", command=edit_table_function).grid(column=1, row=5)
    Button(view_window, text="Done", command=view_window.destroy).grid(column=1, row=6)


def edit_table_function():
    columnname = viview1.get()
    columnvalue = viview2.get()
    orid = viview3.get()

    global mycursor, edit_query
    if columnname == "customername":
        edit_query = "UPDATE orders SET customername=%s WHERE orderid=%s"
    if columnname == "productname":
        edit_query = "UPDATE orders SET productname=%s WHERE orderid=%s"
    if columnname == "customerid":
        edit_query = "UPDATE orders SET customerid=%s WHERE orderid=%s"
    if columnname == "productprice":
        edit_query = "UPDATE orders SET productprice=%s WHERE orderid=%s"
    if columnname == "productquantity":
        edit_query = "UPDATE orders SET productquantity=%s WHERE orderid=%s"

    edit_values_list = []
    list1 = [columnvalue, orid]
    for i in list1:
        edit_values_list.append(i)
    editvalues_tuple = [tuple(edit_values_list)]
    mycursor.executemany(edit_query, editvalues_tuple)
    vidb.commit()


def view_tables():
    global mycursor
    mycursor.execute("Select * From Orders")
    viresult = mycursor.fetchall()

    for row in viresult:
        print(row)
    messagebox.showinfo("Stealth", "Please go to the Output Screen to view the tables")


def close_main_window():
    root.destroy()


def delete_button_function():
    global mycursor
    mycursor.execute("Select * From Orders")
    viresult = mycursor.fetchall()

    for row in viresult:
        print(row)
    messagebox.showinfo("Stealth", "Please go to the Output Screen to view the tables and type in the OrderID to "
                                   "delete that record!")
    top = Toplevel()
    vicanvas = tk.Canvas(top, width=480, height=270)
    vicanvas.grid(columnspan=3, rowspan=4)
    Label(top, text="Please Enter the OrderID to Delete the record.").grid(column=1, row=0)
    global videlete
    videlete = IntVar()

    Entry(top, textvariable=videlete).grid(column=1, row=1)
    Button(top, text="Done", command=deleterow).grid(column=1, row=2)
    Button(top, text="Close", command=top.destroy).grid(column=1, row=3)


def deleterow():
    virow = videlete.get()
    vilist = [virow]
    deletequery = "DELETE FROM orders WHERE orderid=%s"
    mycursor.execute(deletequery, vilist)
    vidb.commit()


# main


vi = Label(root, text="Welcome to Stealth")

vi1 = Label(root, text="What would you like to do today?")

vi.grid(row=0, column=1)

vi1.grid(row=1, column=1)

# Buttons

vibutton1 = Button(root, text="View", command=view_tables, padx=10, pady=10)

vibutton2 = Button(root, text="Add", padx=10, pady=10, command=add_tables)

vibutton3 = Button(root, text="Edit", padx=10, pady=10, command=edit_tables_button)

vibutton4 = Button(root, text="Delete", padx=10, pady=10, command=delete_button_function)

vibutton5 = Button(root, text="Done", padx=10, pady=10, command=close_main_window)

# Button Placement

vibutton1.grid(row=5, column=1)

vibutton2.grid(row=6, column=1)

vibutton3.grid(row=7, column=1)

vibutton4.grid(row=8, column=1)

vibutton5.grid(row=9, column=1)

root.mainloop()
