// Copyright (c) 2023, krantheman and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Balance"] = {
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
  ],
  formatter: (value, row, column, data, default_formatter) => {
    if (
      value &&
      value != "0.00" &&
      (column.fieldname === "in_qty" ||
        column.fieldname === "in_value" ||
        column.fieldname === "out_qty" ||
        column.fieldname === "out_value")
    ) {
      value = default_formatter(value, row, column, data);
      const color = value >= 0 ? "green" : "red";
      value = `<span style='color:${color}!important'>${value}</span>`;
    }
    return value;
  },
};
