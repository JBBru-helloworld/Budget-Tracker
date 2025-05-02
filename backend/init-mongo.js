// MongoDB initialization script
db = db.getSiblingDB("budget_tracker");

// Create collections
db.createCollection("user_profiles");
db.createCollection("receipts");
db.createCollection("categories");

// Insert dummy categories
db.categories.insertMany([
  {
    name: "Groceries",
    icon: "shopping-cart",
    color: "#4CAF50",
  },
  {
    name: "Transportation",
    icon: "car",
    color: "#2196F3",
  },
  {
    name: "Entertainment",
    icon: "film",
    color: "#9C27B0",
  },
  {
    name: "Dining",
    icon: "utensils",
    color: "#FF9800",
  },
  {
    name: "Utilities",
    icon: "home",
    color: "#607D8B",
  },
  {
    name: "Shopping",
    icon: "shopping-bag",
    color: "#E91E63",
  },
  {
    name: "Healthcare",
    icon: "heart",
    color: "#F44336",
  },
  {
    name: "Education",
    icon: "book",
    color: "#673AB7",
  },
]);

// Insert dummy user profile
db.user_profiles.insertOne({
  user_id: "dummy-user-123",
  email: "dummy@example.com",
  display_name: "Dummy User",
  budget_targets: {
    Groceries: 500,
    Transportation: 200,
    Entertainment: 300,
    Dining: 400,
    Utilities: 250,
    Shopping: 300,
    Healthcare: 150,
    Education: 200,
  },
  created_at: new Date(),
  updated_at: new Date(),
});

// Insert dummy receipts
const categories = db.categories.find().toArray();
const dummyUser = db.user_profiles.findOne({ user_id: "Joshua" });

const dummyReceipts = [
  {
    user_id: dummyUser.user_id,
    store_name: "Walmart",
    date: new Date("2024-03-01"),
    total_amount: 125.5,
    items: [
      { name: "Milk", price: 3.99, category: "Groceries" },
      { name: "Bread", price: 2.99, category: "Groceries" },
      { name: "Eggs", price: 4.99, category: "Groceries" },
    ],
    created_at: new Date(),
    updated_at: new Date(),
  },
  {
    user_id: dummyUser.user_id,
    store_name: "Shell Gas Station",
    date: new Date("2024-03-02"),
    total_amount: 45.0,
    items: [{ name: "Gasoline", price: 45.0, category: "Transportation" }],
    created_at: new Date(),
    updated_at: new Date(),
  },
  {
    user_id: dummyUser.user_id,
    store_name: "Netflix",
    date: new Date("2024-03-03"),
    total_amount: 15.99,
    items: [
      { name: "Monthly Subscription", price: 15.99, category: "Entertainment" },
    ],
    created_at: new Date(),
    updated_at: new Date(),
  },
];

db.receipts.insertMany(dummyReceipts);

print("MongoDB initialization completed successfully!");
