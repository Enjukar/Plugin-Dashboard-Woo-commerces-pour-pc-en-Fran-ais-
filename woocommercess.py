import tkinter as tk
from tkinter import ttk, messagebox
import requests
from requests.auth import HTTPBasicAuth

# Remplacez par vos propres clés d'API WooCommerce et URL de votre site
WC_API_URL = 'https://ton site woocommerce'
WC_API_KEY = 'ta clé publique'
WC_API_SECRET = 'ta clé privé 

status_translation = {
    'pending': 'En attente',
    'processing': 'En cours',
    'on-hold': 'En pause',
    'completed': 'Terminé',
    'cancelled': 'Annulé',
    'refunded': 'Remboursé',
    'failed': 'Échoué'
}

def get_orders():
    try:
        response = requests.get(WC_API_URL + 'orders', auth=HTTPBasicAuth(WC_API_KEY, WC_API_SECRET))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur", f"Impossible de récupérer les commandes: {e}")
        return []

def update_order_status(order_id, status):
    data = {"status": status}
    try:
        response = requests.put(WC_API_URL + f'orders/{order_id}', json=data, auth=HTTPBasicAuth(WC_API_KEY, WC_API_SECRET))
        response.raise_for_status()
        messagebox.showinfo("Succès", "Statut de la commande mis à jour avec succès")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur", f"Impossible de mettre à jour le statut de la commande: {e}\nRéponse : {response.text}")

def refresh_orders():
    orders = get_orders()
    for widget in orders_tree.get_children():
        orders_tree.delete(widget)
    for order in orders:
        order_id = order['id']
        order_status = status_translation.get(order['status'], order['status'])
        orders_tree.insert("", "end", values=(order_id, order_status))
    schedule_auto_refresh()

def update_status():
    selected_item = orders_tree.selection()
    if not selected_item:
        messagebox.showerror("Erreur", "Veuillez sélectionner une commande")
        return
    order_id = orders_tree.item(selected_item)['values'][0]
    new_status = [key for key, value in status_translation.items() if value == status_var.get()][0]
    update_order_status(order_id, new_status)
    refresh_orders()

def view_order_details():
    selected_item = orders_tree.selection()
    if not selected_item:
        messagebox.showerror("Erreur", "Veuillez sélectionner une commande")
        return
    order_id = orders_tree.item(selected_item)['values'][0]
    try:
        response = requests.get(WC_API_URL + f'orders/{order_id}', auth=HTTPBasicAuth(WC_API_KEY, WC_API_SECRET))
        response.raise_for_status()
        order = response.json()
        items = order['line_items']
        details = f"Commande ID: {order_id}\nStatut: {status_translation.get(order['status'], order['status'])}\n\nArticles:\n"
        for item in items:
            details += f"- {item['name']} x {item['quantity']}\n"
        messagebox.showinfo("Détails de la commande", details)
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur", f"Impossible de récupérer les détails de la commande: {e}")

def schedule_auto_refresh():
    root.after(90000, refresh_orders)  # Planifie le rafraîchissement automatique toutes les 1.5 minutes

# Configuration de l'interface graphique
root = tk.Tk()
root.title("Tableau de Bord WooCommerce")

main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

orders_tree = ttk.Treeview(main_frame, columns=("ID", "Status"), show="headings")
orders_tree.heading("ID", text="ID de la Commande")
orders_tree.heading("Status", text="Statut")
orders_tree.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))

status_var = tk.StringVar(root)
status_options = ['pending', 'processing', 'on-hold', 'completed', 'cancelled', 'refunded', 'failed']
status_var.set(status_translation[status_options[0]])
status_menu = ttk.OptionMenu(main_frame, status_var, status_translation[status_options[0]], *[status_translation[status] for status in status_options])
status_menu.grid(row=1, column=0, pady=5)

update_button = ttk.Button(main_frame, text="Mettre à jour le statut", command=update_status)
update_button.grid(row=1, column=1, pady=5)

view_button = ttk.Button(main_frame, text="Voir les détails", command=view_order_details)
view_button.grid(row=1, column=2, pady=5)

refresh_button = ttk.Button(main_frame, text="Rafraîchir les commandes", command=refresh_orders)
refresh_button.grid(row=2, column=0, columnspan=3, pady=5)

refresh_orders()  # Initial call to populate the orders
schedule_auto_refresh()  # Schedule the first automatic refresh

root.mainloop()
