// Copyright (c) 2023, krantheman and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stock Entry Item", {
  item(frm, cdt, cdn) {
    validateStock(frm, cdt, cdn, "item");
  },
  src_warehouse(frm, cdt, cdn) {
    validateStock(frm, cdt, cdn, "src_warehouse");
  },
  qty(frm, cdt, cdn) {
    validateStock(frm, cdt, cdn, "qty");
  },
});

const validateStock = async (frm, cdt, cdn, field) => {
  const currentRow = frappe.get_doc(cdt, cdn);
  if (!(currentRow.item && currentRow.src_warehouse && currentRow.qty)) return;
  const outgoingItemQty = totalOutgoingItemQty(currentRow, frm.doc.items);
  const availableItemStock = await getStock(
    currentRow.item,
    currentRow.src_warehouse
  );
  if (availableItemStock < outgoingItemQty) {
    frappe.msgprint({
      title: __(`Inadequte stock of item ${currentRow.item} available`),
      indicator: "red",
      message: __(
        `Warehouse: ${currentRow.src_warehouse} | Available stock: ${availableItemStock} | Outgoing quantity: ${outgoingItemQty}`
      ),
    });
    frappe.model.set_value(cdt, cdn, field, null);
  }
};

const totalOutgoingItemQty = (currentRow, allRows) => {
  let totalQty = 0;
  for (const row of allRows) {
    if (
      row.item === currentRow.item &&
      row.src_warehouse === currentRow.src_warehouse
    )
      totalQty += row.qty;
  }
  return totalQty;
};

const getStock = async (item, warehouse) => {
  return await frappe
    .call({
      method: "inventory_management.inventory_management.api.get_item_stock",
      args: {
        item,
        warehouse,
      },
    })
    .then((r) => r?.message);
};
