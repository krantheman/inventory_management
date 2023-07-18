// Copyright (c) 2023, krantheman and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stock Entry", {
  refresh(frm) {
    updateFields(frm);
  },
  type(frm) {
    updateFields(frm);
  },
});

frappe.ui.form.on("Stock Entry Item", {
  item(frm, cdt, cdn) {
    validateStock(frm, cdt, cdn, "item");
  },
  src_warehouse(frm, cdt, cdn) {
    validateWarehouse(cdt, cdn, "src_warehouse");
    validateStock(frm, cdt, cdn, "src_warehouse");
  },
  tgt_warehouse(frm, cdt, cdn) {
    validateWarehouse(cdt, cdn, "tgt_warehouse");
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

const updateFields = (frm) => {
  if (frm.doc.type === "Consume") {
    updateWarehouseProperties(frm, "src_warehouse", 1);
    updateWarehouseProperties(frm, "tgt_warehouse", 0);
    setUndefinedForUnusedWarehouse(frm, "tgt_warehouse");
  } else if (frm.doc.type === "Receipt") {
    updateWarehouseProperties(frm, "tgt_warehouse", 1);
    updateWarehouseProperties(frm, "src_warehouse", 0);
    setUndefinedForUnusedWarehouse(frm, "src_warehouse");
  } else {
    updateWarehouseProperties(frm, "src_warehouse", 1);
    updateWarehouseProperties(frm, "tgt_warehouse", 1);
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

const setUndefinedForUnusedWarehouse = (frm, field) => {
  for (const row of frm.doc.items) {
    frappe.model.set_value("Stock Entry Item", row.name, field, undefined);
  }
};
