// Copyright (c) 2023, krantheman and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Ledger"] = {
  filters: [
    {
      fieldname: "from_date",
      label: __("From"),
      fieldtype: "Date",
    },
    {
      fieldname: "to_date",
      label: __("To"),
      fieldtype: "Date",
    },
    ,
    {
      fieldname: "item",
      label: __("Item"),
      fieldtype: "Link",
      options: "Item",
    },
    {
      fieldname: "warehouse",
      label: __("Warehouse"),
      fieldtype: "Link",
      options: "Warehouse",
    },
    {
      fieldname: "type",
      label: __("Type"),
      fieldtype: "Select",
      options: ["", "Incoming", "Outgoing"],
    },
    {
      fieldname: "stock_entry",
      label: __("Stock Entry"),
      fieldtype: "Link",
      options: "Stock Entry",
    },
  ],
  formatter: (value, row, column, data, default_formatter) => {
    if (
      column.fieldname === "qty_change" ||
      column.fieldname === "value_change"
    ) {
      value = default_formatter(value, row, column, data);
      const color = value >= 0 ? "green" : "red";
      value = `<span style='color:${color}!important'>${value}</span>`;
    }
    return value;
  },
};
