import { open } from "sqlite";
import sqlite3 from "sqlite3";

import { createSchema } from "./schema.js";
import { getPendingOrders } from "./queries/order_queries.js";

async function main() {
  const db = await open({
    filename: "ecommerce.db",
    driver: sqlite3.Database,
  });

  await createSchema(db, false);

  // Get and print orders pending longer than 3 days
  const pendingOrders = await getPendingOrders(db);
  const overdueOrders = pendingOrders.filter(order => order.days_since_created > 3);

  console.log(`Found ${overdueOrders.length} orders pending longer than 3 days:`);

  overdueOrders.forEach(order => {
    console.log(`- Order ID: ${order.order_id}, Customer: ${order.customer_name}, ` +
      `Days Pending: ${order.days_since_created.toFixed(1)}, ` +
      `Amount: $${order.total_amount}`);
  });

}

main();