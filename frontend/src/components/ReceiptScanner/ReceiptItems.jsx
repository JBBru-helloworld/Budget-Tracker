import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import apiService from "../../services/apiService";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import { Loader, Save, Plus, Minus } from "lucide-react";

const ReceiptItems = ({ items, receiptImage }) => {
  const { user } = useAuth();
  const [receiptItems, setReceiptItems] = useState([]);
  const [sharedUsers, setSharedUsers] = useState([
    { id: "me", name: "Me", items: [] },
    { id: "other", name: "Add Person", items: [] },
  ]);
  const [categories, setCategories] = useState([]);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [newPersonName, setNewPersonName] = useState("");
  const [showAddPerson, setShowAddPerson] = useState(false);

  useEffect(() => {
    // Initialize items with default category and cost
    setReceiptItems(
      items.map((item, index) => ({
        id: `item-${index}`,
        name: item.name,
        price: item.price || 0,
        categoryId: "",
        assignedTo: null,
      }))
    );

    // Fetch available categories
    fetchCategories();
  }, [items]);

  const fetchCategories = async () => {
    try {
      const response = await apiService.get("/categories");
      setCategories(response.data);
    } catch (err) {
      console.error("Failed to fetch categories:", err);
    }
  };

  const handleDragEnd = (result) => {
    const { source, destination, draggableId } = result;

    // Dropped outside a droppable area
    if (!destination) return;

    // Item was dropped in its original location
    if (
      source.droppableId === destination.droppableId &&
      source.index === destination.index
    )
      return;

    // Find the item being dragged
    const draggedItem = receiptItems.find((item) => item.id === draggableId);

    // Update shared users and receipt items
    const updatedSharedUsers = [...sharedUsers];
    const sourceUser = updatedSharedUsers.find(
      (user) => user.id === source.droppableId
    );
    const destUser = updatedSharedUsers.find(
      (user) => user.id === destination.droppableId
    );

    // If item was previously assigned to someone
    if (sourceUser && sourceUser.id !== "unassigned") {
      sourceUser.items = sourceUser.items.filter(
        (itemId) => itemId !== draggableId
      );
    }

    // Assign to new user
    if (destUser && destUser.id !== "unassigned") {
      destUser.items.push(draggableId);
    }

    // Update the item's assignedTo property
    const updatedReceiptItems = receiptItems.map((item) => {
      if (item.id === draggableId) {
        return {
          ...item,
          assignedTo:
            destination.droppableId === "unassigned"
              ? null
              : destination.droppableId,
        };
      }
      return item;
    });

    setSharedUsers(updatedSharedUsers);
    setReceiptItems(updatedReceiptItems);
  };

  const handleCategoryChange = (itemId, categoryId) => {
    setReceiptItems(
      receiptItems.map((item) => {
        if (item.id === itemId) {
          return { ...item, categoryId };
        }
        return item;
      })
    );
  };

  const handlePriceChange = (itemId, price) => {
    const numericPrice = parseFloat(price) || 0;
    setReceiptItems(
      receiptItems.map((item) => {
        if (item.id === itemId) {
          return { ...item, price: numericPrice };
        }
        return item;
      })
    );
  };

  const addNewPerson = () => {
    if (!newPersonName.trim()) return;

    const newId = `person-${Date.now()}`;
    setSharedUsers([
      ...sharedUsers.filter((u) => u.id !== "other"), // Remove the "Add Person" option
      { id: newId, name: newPersonName, items: [] },
      { id: "other", name: "Add Person", items: [] }, // Add it back at the end
    ]);

    setNewPersonName("");
    setShowAddPerson(false);
  };

  const calculateTotal = (userId) => {
    const user = sharedUsers.find((u) => u.id === userId);
    if (!user) return 0;

    return user.items.reduce((total, itemId) => {
      const item = receiptItems.find((i) => i.id === itemId);
      return total + (item?.price || 0);
    }, 0);
  };

  const saveReceipt = async () => {
    setIsSaving(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("image", receiptImage);

      // Create receipt metadata
      const receiptData = {
        items: receiptItems.map((item) => ({
          name: item.name,
          price: item.price,
          categoryId: item.categoryId || null,
          assignedTo: item.assignedTo === "me" ? user.id : item.assignedTo,
        })),
        sharedWith: sharedUsers
          .filter((user) => user.id !== "me" && user.id !== "other")
          .map((user) => ({
            name: user.name,
            items: user.items,
          })),
      };

      formData.append("data", JSON.stringify(receiptData));

      await apiService.post("/receipts", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      console.error("Failed to save receipt:", err);
      setError(
        err.response?.data?.message ||
          "Failed to save receipt. Please try again."
      );
    } finally {
      setIsSaving(false);
    }
  };

  const getTotalReceiptAmount = () => {
    return receiptItems.reduce((total, item) => total + (item.price || 0), 0);
  };

  const getUnassignedItems = () => {
    return receiptItems.filter((item) => !item.assignedTo);
  };

  return (
    <div className="mt-8 bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Receipt Items</h3>

      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="flex flex-col md:flex-row gap-6">
          {/* Unassigned items list */}
          <div className="flex-1">
            <h4 className="font-medium text-gray-700 mb-2">Unassigned Items</h4>
            <Droppable droppableId="unassigned">
              {(provided) => (
                <div
                  {...provided.droppableProps}
                  ref={provided.innerRef}
                  className="bg-gray-50 p-3 rounded-md min-h-40 border border-gray-200"
                >
                  {getUnassignedItems().map((item, index) => (
                    <Draggable
                      key={item.id}
                      draggableId={item.id}
                      index={index}
                    >
                      {(provided) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          className="bg-white p-3 mb-2 rounded-md shadow-sm border border-gray-100 flex flex-col"
                        >
                          <div className="flex justify-between items-center">
                            <span className="font-medium">{item.name}</span>
                            <div className="flex items-center">
                              <span className="text-gray-600 mr-1">$</span>
                              <input
                                type="number"
                                value={item.price}
                                onChange={(e) =>
                                  handlePriceChange(item.id, e.target.value)
                                }
                                className="w-20 p-1 text-right border border-gray-200 rounded"
                                min="0"
                                step="0.01"
                              />
                            </div>
                          </div>
                          <div className="mt-2">
                            <select
                              value={item.categoryId}
                              onChange={(e) =>
                                handleCategoryChange(item.id, e.target.value)
                              }
                              className="w-full p-2 border border-gray-200 rounded text-sm"
                            >
                              <option value="">Select category</option>
                              {categories.map((category) => (
                                <option key={category.id} value={category.id}>
                                  {category.name}
                                </option>
                              ))}
                            </select>
                          </div>
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                  {getUnassignedItems().length === 0 && (
                    <div className="text-center py-4 text-gray-500">
                      All items have been assigned
                    </div>
                  )}
                </div>
              )}
            </Droppable>
          </div>

          {/* People columns */}
          <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4">
            {sharedUsers.map((user) => (
              <div key={user.id} className="flex flex-col">
                {user.id === "other" ? (
                  // Add Person column
                  <div className="h-full">
                    <h4 className="font-medium text-gray-700 mb-2">
                      {showAddPerson ? (
                        "Add Person"
                      ) : (
                        <button
                          onClick={() => setShowAddPerson(true)}
                          className="flex items-center text-blue-600 hover:text-blue-800"
                        >
                          <Plus className="w-4 h-4 mr-1" />
                          Add Person
                        </button>
                      )}
                    </h4>

                    {showAddPerson && (
                      <div className="bg-gray-50 p-3 rounded-md border border-gray-200">
                        <div className="flex mb-2">
                          <input
                            type="text"
                            value={newPersonName}
                            onChange={(e) => setNewPersonName(e.target.value)}
                            placeholder="Person's name"
                            className="flex-1 p-2 border border-gray-300 rounded-l-md"
                          />
                          <button
                            onClick={addNewPerson}
                            className="bg-blue-600 text-white px-3 py-2 rounded-r-md hover:bg-blue-700"
                          >
                            Add
                          </button>
                        </div>
                        <button
                          onClick={() => setShowAddPerson(false)}
                          className="text-gray-500 text-sm hover:text-gray-700"
                        >
                          Cancel
                        </button>
                      </div>
                    )}
                  </div>
                ) : (
                  // Regular person column
                  <>
                    <div className="flex justify-between mb-2">
                      <h4 className="font-medium text-gray-700">{user.name}</h4>
                      <span className="font-bold text-blue-600">
                        ${calculateTotal(user.id).toFixed(2)}
                      </span>
                    </div>
                    <Droppable droppableId={user.id}>
                      {(provided) => (
                        <div
                          {...provided.droppableProps}
                          ref={provided.innerRef}
                          className="bg-gray-50 p-3 rounded-md min-h-40 flex-1 border border-gray-200"
                        >
                          {user.items.map((itemId, index) => {
                            const item = receiptItems.find(
                              (i) => i.id === itemId
                            );
                            if (!item) return null;

                            return (
                              <Draggable
                                key={item.id}
                                draggableId={item.id}
                                index={index}
                              >
                                {(provided) => (
                                  <div
                                    ref={provided.innerRef}
                                    {...provided.draggableProps}
                                    {...provided.dragHandleProps}
                                    className="bg-white p-3 mb-2 rounded-md shadow-sm border border-gray-100 flex flex-col"
                                  >
                                    <div className="flex justify-between items-center">
                                      <span className="font-medium">
                                        {item.name}
                                      </span>
                                      <div className="flex items-center">
                                        <span className="text-gray-600 mr-1">
                                          $
                                        </span>
                                        <input
                                          type="number"
                                          value={item.price}
                                          onChange={(e) =>
                                            handlePriceChange(
                                              item.id,
                                              e.target.value
                                            )
                                          }
                                          className="w-20 p-1 text-right border border-gray-200 rounded"
                                          min="0"
                                          step="0.01"
                                        />
                                      </div>
                                    </div>
                                    <div className="mt-2">
                                      <select
                                        value={item.categoryId}
                                        onChange={(e) =>
                                          handleCategoryChange(
                                            item.id,
                                            e.target.value
                                          )
                                        }
                                        className="w-full p-2 border border-gray-200 rounded text-sm"
                                      >
                                        <option value="">
                                          Select category
                                        </option>
                                        {categories.map((category) => (
                                          <option
                                            key={category.id}
                                            value={category.id}
                                          >
                                            {category.name}
                                          </option>
                                        ))}
                                      </select>
                                    </div>
                                  </div>
                                )}
                              </Draggable>
                            );
                          })}
                          {provided.placeholder}
                          {user.items.length === 0 && (
                            <div className="text-center py-4 text-gray-500">
                              Drag items here
                            </div>
                          )}
                        </div>
                      )}
                    </Droppable>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      </DragDropContext>

      <div className="mt-6 flex justify-between items-center">
        <div className="text-xl font-bold">
          Total: ${getTotalReceiptAmount().toFixed(2)}
        </div>
        <button
          onClick={saveReceipt}
          disabled={isSaving}
          className={`px-6 py-2 ${
            isSaving ? "bg-gray-400" : "bg-green-600 hover:bg-green-700"
          } text-white rounded-md transition flex items-center`}
        >
          {isSaving ? (
            <>
              <Loader className="w-5 h-5 mr-2 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="w-5 h-5 mr-2" />
              Save Receipt
            </>
          )}
        </button>
      </div>

      {/* Error message */}
      {error && (
        <div className="mt-4 p-3 bg-red-100 text-red-800 rounded-md">
          {error}
        </div>
      )}

      {/* Success message */}
      {saveSuccess && (
        <div className="mt-4 p-3 bg-green-100 text-green-800 rounded-md">
          Receipt saved successfully!
        </div>
      )}
    </div>
  );
};

export default ReceiptItems;
