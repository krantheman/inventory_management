// Copyright (c) 2023, krantheman and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stock Entry Item", {
  item(frm, cdt, cdn) {
    console.log("hello")
    // frm.call("get_stock", { throw_if_missing: true }).then((r) => {
    //   console.log(r);
    // });
  },
});

const outgoingItems = (items) => {
  items = items.map((item) => ({
    item: item.item,
    src_warehouse: item.src_warehouse,
    qty: item.qty,
  }));
  return groupItems(items);
};

const groupItems = (items) => {
  const grouped = {};
  for (const obj of items) {
    const { item, src_warehouse, qty } = obj;
    const key = `${item}-${src_warehouse}`;
    if (!grouped[key]) {
      grouped[key] = { item, src_warehouse, qty: 0 };
    }
    grouped[key].qty += qty;
  }
  return Object.values(grouped);
};

const getStock = () => {
  frm.call("get_stock", { throw_if_missing: true }).then((r) => {
    console.log(r);
  });
};
