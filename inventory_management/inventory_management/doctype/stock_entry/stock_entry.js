// Copyright (c) 2023, krantheman and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stock Entry", {
  onload_post_render(frm) {
    updateFields(frm);
  },
  type(frm) {
    updateFields(frm);
  },
});

frappe.ui.form.on("Stock Entry Item", {
  item(frm, cdt, cdn) {
    validateStock(frm, cdt, cdn, "item");
    setValuationRate(frm, cdt, cdn);
  },
  src_warehouse(frm, cdt, cdn) {
    validateWarehouse(cdt, cdn, "src_warehouse");
    validateStock(frm, cdt, cdn, "src_warehouse");
    setValuationRate(frm, cdt, cdn);
  },
  tgt_warehouse(frm, cdt, cdn) {
    validateWarehouse(cdt, cdn, "tgt_warehouse");
    if (frm.doc.type === "Receipt") setValuationRate(frm, cdt, cdn);
  },
  qty(frm, cdt, cdn) {
    validateQty(frm, cdt, cdn);
  },
  rate(frm, cdt, cdn) {
    validateRate(cdt, cdn);
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
    frappe.model.set_value(cdt, cdn, field, undefined);
  }
};

const validateWarehouse = (cdt, cdn, field) => {
  const currentRow = frappe.get_doc(cdt, cdn);
  if (
    currentRow.src_warehouse &&
    currentRow.src_warehouse === currentRow.tgt_warehouse
  ) {
    frappe.model.set_value(cdt, cdn, field, undefined);
    frappe.throw("Source and target warehouse cannot be the same");
  }
};

const validateQty = (frm, cdt, cdn) => {
  if (frappe.get_doc(cdt, cdn).qty <= 0) {
    frappe.model.set_value(cdt, cdn, "qty", undefined);
  } else {
    validateStock(frm, cdt, cdn, "qty");
  }
};

const validateRate = (cdt, cdn) => {
  if (frappe.get_doc(cdt, cdn).rate <= 0) {
    frappe.model.set_value(cdt, cdn, "rate", undefined);
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

const updateFields = (frm) => {
  if (frm.doc.type === "Consume") {
    updateWarehouseProperties(frm, "src_warehouse", 1);
    updateWarehouseProperties(frm, "tgt_warehouse", 0);
    updateItemFields(frm, "tgt_warehouse");
    frm.fields_dict.items.grid.update_docfield_property("rate", "read_only", 1);
  } else if (frm.doc.type === "Receipt") {
    updateWarehouseProperties(frm, "tgt_warehouse", 1);
    updateWarehouseProperties(frm, "src_warehouse", 0);
    updateItemFields(frm, "src_warehouse");
    frm.fields_dict.items.grid.update_docfield_property("rate", "read_only", 0);
  } else {
    updateWarehouseProperties(frm, "src_warehouse", 1);
    updateWarehouseProperties(frm, "tgt_warehouse", 1);
    frm.fields_dict.items.grid.update_docfield_property("rate", "read_only", 1);
  }
};

const updateWarehouseProperties = (frm, warehouse, reqd) => {
  frm.fields_dict.items.grid.update_docfield_property(warehouse, "reqd", reqd);
  frm.fields_dict.items.grid.update_docfield_property(
    warehouse,
    "read_only",
    1 - reqd
  );
};

const updateItemFields = (frm, field) => {
  for (const row of frm.doc.items) {
    frappe.model.set_value("Stock Entry Item", row.name, field, undefined);
    if (frm.doc.type === "Receipt")
      setValuationRate(frm, "Stock Entry Item", row.name);
  }
};

const setValuationRate = async (frm, cdt, cdn) => {
  const currentRow = frappe.get_doc(cdt, cdn);
  const warehouse =
    frm.doc.type === "Receipt"
      ? currentRow.tgt_warehouse
      : currentRow.src_warehouse;
  if (!(currentRow.item && warehouse)) return;
  const valuationRate = await getValuationRate(currentRow.item, warehouse);
  frappe.model.set_value(cdt, cdn, "rate", valuationRate);
};

const getStock = async (item, warehouse) => {
  return await frappe
    .call({
      method: "inventory_management.inventory_management.utils.get_item_stock",
      args: {
        item,
        warehouse,
      },
    })
    .then((r) => r?.message);
};

const getValuationRate = async (item, warehouse) => {
  return await frappe
    .call({
      method:
        "inventory_management.inventory_management.utils.get_valuation_rate",
      args: {
        item,
        warehouse,
      },
    })
    .then((r) => r?.message);
};
