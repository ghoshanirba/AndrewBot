import axios, { all } from "axios";
import React, { useEffect, useState, MouseEvent } from "react";
import { useLocation } from "react-router-dom";
import "./CreateOrderPage.css";
// import { Modal, Button } from "bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTrashCan } from "@fortawesome/free-solid-svg-icons";

interface APIResponse {
  tabs: Tabs;
}

interface Tabs {
  product_info: ProductInfo;
  total_count_of_all_products: number;
}

interface ProductInfo {
  products: Product[];
}

interface Product {
  id: number;
  name: string;
  weight: string;
  magnitude: number;
  magnitude_unit: string;
  pricing: Pricing;
  brand: Brand;
  category: Category;
  keep_selected: string;
  children?: Product[]; //Optional field as it will be present for only main product.
  total_count_of_one_product_with_children?: number; // Optional field since it's only present in the main product
  quantity?: number;
}

interface Pricing {
  mrp: number;
  selling_price: number;
  discount: string;
}

interface Brand {
  name: string;
}

interface Category {
  tlc_name: string;
  mlc_name: string;
  ilc_name: string;
}

interface ProductModalProps {
  parentProductID: number;
  product: userSelectedProducts[];
  onClose: () => void;
}

interface TableHeaderProps {
  lastColumnName: string;
  showModal: boolean;
}

interface TableRowProps {
  product: userSelectedProducts;
  showModal: boolean;
  index: number;
  parentOrChild: "parent" | "child";
}

interface userSelectedProducts {
  id: number;
  name: string;
  weight: string;
  magnitude: number;
  magnitude_unit: string;
  pricing: Pricing;
  brand: Brand;
  category: Category;
  keep_selected: string;
  quantity?: number;
  totalMRP?: number;
  netSellingPrice?: number;
  totalDiscount?: number;
}

interface createOrderAPIcallInterface {
  userID: string;
  products: userSelectedProducts[];
  orderConfirmedByUser: string;
  orderCreatedDate: string;
  orderFulfilled: string;
  orderFulfillmentDate: string;
  totalAmountMRP: number;
  totalDiscountAmount: number;
  netTotalAmount: number;
  billingAddress: Address;
  shippingAddress: Address;
  paymentMethod: string;
  estimatedOrderFulfillmentDate: string;
}

interface Address {
  houseNumber: string;
  buildingName: string;
  street: string;
  addressLine1: string;
  addressLine2: string;
  addressLine3: string;
  city: string;
  state: string;
  pincode: number;
  landMark: string;
  country: string;
}

export default function CreateOrderPage() {
  const API_URL = "http://127.0.0.1:5000";
  // const location = useLocation();
  const [orderResponse, setOrderResponse] = useState<APIResponse | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentDate, setCurrentDate] = useState<string>("");
  const [loadMoreClicked, setLoadMoreClicked] = useState(false);
  const [displayProducts, setDisplayProducts] = useState<
    userSelectedProducts[]
  >([]);
  const [userSelectedProducts, setUserSelectedProducts] = useState<
    userSelectedProducts[]
  >([]);
  const [userSelectedProductsMap, setUserSelectedProductsMap] = useState<
    Map<number, userSelectedProducts>
  >(new Map());

  const [selectedParentProductID, setSelectedParentProductID] =
    useState<number>();
  const [showModal, setShowModal] = useState(false);
  const [selectedProduct, setSelectedProduct] =
    useState<userSelectedProducts>(); //state for selected product for Load More options
  const [selectAll, setSelectAll] = useState(false);

  const [modalDisplayProducts, setModalDisplayProducts] = useState<
    userSelectedProducts[]
  >([]);
  const [modalSelectedProducts, setModalSelectedProducts] = useState<
    userSelectedProducts[]
  >([]);
  const [modalSelectedProductsMap, setModalSelectedProductsMap] = useState<
    Map<number, userSelectedProducts>
  >(new Map());
  const [modalParentChild, setModalParentChild] = useState<Product>();
  const [selectAllModal, setSelectAllModal] = useState(false);

  const [isConfirmedByUser, setIsConfirmedByUser] = useState(false); //State to determine whether user has confirmed the order or not.
  const [orderID, setOrderID] = useState(null); //State for orderID generation
  const [showModalOrderID, setShowModalOrderID] = useState(false);

  // Get current date function
  const getCurrentDate = () => {
    const today = new Date();
    const formatDate = today.toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
    console.log("formatDate:", formatDate);
    return formatDate;
  };

  //Initial useEffect() call after receiving the order details from the user. BEGINNING
  //***********************************************************************************//
  useEffect(() => {
    // Directly access localStorage and parse the data
    const storedCreateOrderDetails = localStorage
      .getItem("createOrderDetails")
      ?.trim();

    if (storedCreateOrderDetails) {
      localStorage.removeItem("createOrderDetails");
    }

    console.log("storedCreateOrderDetails: ", storedCreateOrderDetails);

    const composeOrder = async (orderDetails: string) => {
      try {
        console.log("composeOrderData:", orderDetails);

        const params = {
          orderDetails: orderDetails,
        };

        console.log("query params:", params);

        // The API OrderManagementAPI will receive the order details in below format for GET API call.
        // The request will have "orderDetails" key added to it.
        // {
        //   "orderDetails":"wheat, ashirbaad, 5 kg, chatu, mana, 200 grams, rice flour, bb royal, 100 gms"
        // }
        const response = await axios.get(`${API_URL}/orders/compose`, {
          params: params,
        });

        console.log(response);

        if (response.status === 200) {
          // console.log("API response:", response.data); // Log response data directly
          setOrderResponse(response.data); // Update state with response data
        } else {
          // Handle non-200 status codes
          console.error("Error: Received non-200 status code", response.status);
        }
      } catch (error) {
        setError("Error fetching order details");
        console.error("Error fetching order details:", error);
      } finally {
        setLoading(false);
      }
    };

    // Get the current date
    setCurrentDate(getCurrentDate());

    // calling function createOrder() using createOrderData
    if (storedCreateOrderDetails) {
      composeOrder(storedCreateOrderDetails);
    }
  }, []);
  //Initial useEffect() call after receiving the order details from the user. END
  //******************************************************************************/

  // 2nd useEffect() call to Process the response.data from the backend API. BEGINNING
  //***********************************************************************************/
  useEffect(() => {
    // console.log("within order response useEffect hook")
    if (orderResponse && "tabs" in orderResponse) {
      const apiResponse = orderResponse as APIResponse; // Type assertion to APIResponse
      // console.log("API response tabs:", apiResponse.tabs.product_info); // Access tabs from the API response
      setProducts(apiResponse.tabs.product_info.products);

      const initialSelectedProducts: userSelectedProducts[] =
        apiResponse.tabs.product_info.products
          .filter((products) => products.keep_selected === "Y")
          .map((products) => {
            const quantity = 1; //Assuming the initial quantity as 1.
            const totalMRP = quantity * products.pricing.mrp;
            const netSellingPrice = quantity * products.pricing.selling_price;
            const totalDiscount = totalMRP - netSellingPrice;

            return {
              id: products.id,
              name: products.name,
              weight: products.weight,
              magnitude: products.magnitude,
              magnitude_unit: products.magnitude_unit,
              pricing: products.pricing,
              brand: products.brand,
              category: products.category,
              keep_selected: products.keep_selected,
              quantity: quantity,
              totalMRP: totalMRP,
              netSellingPrice: netSellingPrice,
              totalDiscount: totalDiscount,
            };
          });

      // Update userSelectedProducts with the array - these are the initial recommended choices
      setUserSelectedProducts(initialSelectedProducts);
      setDisplayProducts(initialSelectedProducts);

      //Build a Map out of the initial recommended product choices
      const initialSelectedProductsMap = new Map<number, userSelectedProducts>(
        initialSelectedProducts.map((product) => [product.id, product])
      );

      // Update userSelectedProductsMap with the initialSelectedProductsMap
      setUserSelectedProductsMap(initialSelectedProductsMap);
    }
  }, [orderResponse]);
  // 2nd useEffect() call to Process the response.data from the backend API. END
  //****************************************************************************/

  //useEffect() hook to display Modal after clicking on Load More from the Main Page. BEGINNING
  //*******************************************************************************************/
  useEffect(() => {
    if (modalDisplayProducts.length > 0) {
      setShowModal(true);
    }
  }, [modalDisplayProducts]);
  //useEffect() hook to display Modal after clicking on Load More from the Main Page. END
  //*************************************************************************************/

  //useEffect hook to show the orderID to the user as a pop-up Modal.
  useEffect(() => {
    if (isConfirmedByUser && orderID) {
      setShowModalOrderID(true);
    }
  }, [isConfirmedByUser, orderID]);

  const handleCloseModalOrderID = () => {
    setShowModalOrderID(false);
  };

  console.log("1st userSelectedProducts:", userSelectedProducts);
  // console.log("1st userSelectedProductsMap:", userSelectedProductsMap)

  // Table Header Component
  function TableHeader({ lastColumnName, showModal }: TableHeaderProps) {
    const handleSelectAllChange = (
      event: React.ChangeEvent<HTMLInputElement>
    ) => {
      const isChecked = event.target.checked;

      setSelectAll(isChecked);
      const updatedUserSelectedProductsMap = new Map(userSelectedProductsMap);

      if (isChecked) {
        //Select All, add all products from displayProducts to userSelectedProducts & userSelectedProductsMap
        displayProducts.forEach((product) => {
          updatedUserSelectedProductsMap.set(product.id, product);
        });
      } else {
        displayProducts.forEach((product) => {
          if (updatedUserSelectedProductsMap.has(product.id)) {
            updatedUserSelectedProductsMap.delete(product.id);
          }
        });
      }
      setUserSelectedProductsMap(updatedUserSelectedProductsMap);

      setUserSelectedProducts(
        Array.from(updatedUserSelectedProductsMap.values())
      );
    };

    const handleSelectAllChangeModal = (
      event: React.ChangeEvent<HTMLInputElement>
    ) => {
      const isCheckedModal = event.target.checked;
      setSelectAllModal(isCheckedModal);

      const updatedModalSelectedProductsMap = new Map(modalSelectedProductsMap);

      if (isCheckedModal) {
        modalDisplayProducts.forEach((product) => {
          updatedModalSelectedProductsMap.set(product.id, product);
        });
      } else {
        modalDisplayProducts.forEach((product) => {
          if (updatedModalSelectedProductsMap.has(product.id)) {
            updatedModalSelectedProductsMap.delete(product.id);
          }
        });
      }

      setModalSelectedProductsMap(updatedModalSelectedProductsMap);
      setModalSelectedProducts(
        Array.from(updatedModalSelectedProductsMap.values())
      );
    };

    useEffect(() => {
      //check whether all rows are selected or not
      const allRowsSelected = displayProducts.every((product) =>
        userSelectedProductsMap.has(product.id)
      );

      //if all rows are selected then update selectAll state
      if (allRowsSelected !== selectAll) {
        setSelectAll(allRowsSelected);
      }
    }, [displayProducts, userSelectedProductsMap, selectAll, !showModal]);

    useEffect(() => {
      //check whether all rows are selected or not for Modal
      const allRowsSelectedModal = modalDisplayProducts.every((product) =>
        modalSelectedProductsMap.has(product.id)
      );

      //if all rows are selected then update selectAll state
      if (allRowsSelectedModal !== selectAllModal) {
        setSelectAllModal(allRowsSelectedModal);
      }
    }, [
      modalDisplayProducts,
      modalSelectedProductsMap,
      selectAllModal,
      showModal,
    ]);

    return (
      <thead>
        <tr className="table-secondary">
          {!showModal ? (
            <th
              className="table-header-font"
              scope="col"
              style={{ textAlign: "center", verticalAlign: "middle" }}
            >
              <input
                type="checkbox"
                id="selectAll"
                checked={selectAll}
                onChange={handleSelectAllChange}
                disabled={isConfirmedByUser}
              />
            </th>
          ) : (
            <th
              className="table-header-font"
              scope="col"
              style={{ textAlign: "center", verticalAlign: "middle" }}
            >
              <input
                type="checkbox"
                id="selectAllModal"
                checked={selectAllModal}
                onChange={handleSelectAllChangeModal}
                disabled={isConfirmedByUser}
              />
            </th>
          )}
          <th
            className="table-header-font"
            scope="col"
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            Product Name
          </th>
          <th
            className="table-header-font"
            scope="col"
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            Brand
          </th>
          <th
            className="table-header-font"
            scope="col"
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            Weight
          </th>
          <th
            className="table-header-font"
            scope="col"
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            Quantity
          </th>
          <th
            className="table-header-font"
            scope="col"
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            MRP Per Unit
          </th>
          {/* <th className="table-header-font" scope="col">
                  Total Price(MRP)
                </th> */}
          <th
            className="table-header-font"
            scope="col"
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            Discount Per Unit
          </th>
          {/* <th className="table-header-font" scope="col">
                  Total Discount
                </th> */}
          <th
            className="table-header-font"
            scope="col"
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            Selling Price Per Unit
          </th>
          {!showModal && (
            <>
              <th
                className="table-header-font"
                scope="col"
                style={{ textAlign: "center", verticalAlign: "middle" }}
              >
                Total MRP
              </th>
              <th
                className="table-header-font"
                scope="col"
                style={{ textAlign: "center", verticalAlign: "middle" }}
              >
                Total Discount
              </th>
              <th
                className="table-header-font"
                scope="col"
                style={{ textAlign: "center", verticalAlign: "middle" }}
              >
                Net Selling Price
              </th>
            </>
          )}
          <th
            className="table-header-font"
            scope="col"
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            {lastColumnName}
          </th>

          {!showModal && (
            <th
              className="table-header-font"
              scope="col"
              style={{ textAlign: "center", verticalAlign: "middle" }}
            >
              Delete
            </th>
          )}
        </tr>
      </thead>
    );
  }

  // Table Row Component
  function TableRow({
    product,
    showModal,
    index,
    parentOrChild,
  }: TableRowProps) {
    console.log("within TableRow component:", parentOrChild);
    console.log("product1:", product);

    const handleCheckBoxChange = (
      product: userSelectedProducts,
      checked: boolean
    ) => {
      // console.log("product2:", product)
      const quantity = product.quantity || 1;
      const totalMRP = quantity * product.pricing.mrp;
      const netSellingPrice = quantity * product.pricing.selling_price;
      const totalDiscount = totalMRP - netSellingPrice;

      if (!showModal) {
        setUserSelectedProductsMap((prevUserSelectedProductsMap) => {
          //Create a Map from the previous state
          const updatedUserSelectedProductsMap = new Map(
            prevUserSelectedProductsMap
          );

          if (checked) {
            // If checked, add or update the product with its current quantity
            updatedUserSelectedProductsMap.set(product.id, {
              ...product,
              quantity: quantity,
              totalMRP: totalMRP,
              netSellingPrice: netSellingPrice,
              totalDiscount: totalDiscount,
            });
          } else {
            // If unchecked, remove the product from the Map
            updatedUserSelectedProductsMap.delete(product.id);
          }

          // Extract the value part from userSelectedProductsMap, and update the userSelectedProducts state
          setUserSelectedProducts(
            Array.from(updatedUserSelectedProductsMap.values())
          );

          return updatedUserSelectedProductsMap;
        });
      }

      if (showModal) {
        setModalSelectedProductsMap((prevModalSelectedProductsMap) => {
          //Create a Map from the previous state
          const updatedmodalSelectedProductsMap = new Map(
            prevModalSelectedProductsMap
          );

          if (checked) {
            updatedmodalSelectedProductsMap.set(product.id, {
              ...product,
              quantity: quantity,
              totalMRP: totalMRP,
              netSellingPrice: netSellingPrice,
              totalDiscount: totalDiscount,
            });
          } else {
            updatedmodalSelectedProductsMap.delete(product.id);
          }

          // Create an array out of the Map
          setModalSelectedProducts(
            Array.from(updatedmodalSelectedProductsMap.values())
          );

          return updatedmodalSelectedProductsMap;
        });
      }
    };

    // HTMLSelectElement event for dropdown selects
    const handleQuantityChange = (
      product: userSelectedProducts,
      event: React.ChangeEvent<HTMLSelectElement>
    ) => {
      //event.target.value is a string. converting a string to base 10 integer
      // console.log("product3:", product)
      const quantity = parseInt(event.target.value, 10);
      const totalMRP = quantity * product.pricing.mrp;
      const netSellingPrice = quantity * product.pricing.selling_price;
      const totalDiscount = totalMRP - netSellingPrice;

      //Update the quantity in the products array
      if (!showModal) {
        setDisplayProducts((prevDisplayedProducts) => {
          return prevDisplayedProducts.map((p) => {
            if (p.id === product.id) {
              return {
                ...p,
                quantity: quantity,
                totalMRP: totalMRP,
                netSellingPrice: netSellingPrice,
                totalDiscount: totalDiscount,
              };
            } else {
              return p;
            }
          });
        });
      }

      if (showModal) {
        setModalDisplayProducts((prevModalDisplayedProducts) => {
          return prevModalDisplayedProducts.map((p) => {
            if (p.id === product.id) {
              return {
                ...p,
                quantity: quantity,
                totalMRP: totalMRP,
                netSellingPrice: netSellingPrice,
                totalDiscount: totalDiscount,
              };
            } else {
              return p;
            }
          });
        });
      }

      //Modify the states of the selected products if there is any quantity change
      if (userSelectedProductsMap.has(product.id)) {
        setUserSelectedProductsMap((prevUserSelectedProductsMap) => {
          const updatedUserSelectedProductsMap = new Map(
            prevUserSelectedProductsMap
          );

          const existingUserSelectedProduct =
            updatedUserSelectedProductsMap.get(product.id);

          if (existingUserSelectedProduct) {
            updatedUserSelectedProductsMap.set(product.id, {
              ...existingUserSelectedProduct,
              quantity: quantity,
              totalMRP: totalMRP,
              netSellingPrice: netSellingPrice,
              totalDiscount: totalDiscount,
            });
          }

          const updatedUserSelectedProducts = Array.from(
            updatedUserSelectedProductsMap.values()
          );
          setUserSelectedProducts(updatedUserSelectedProducts);

          return updatedUserSelectedProductsMap;
        });
      }

      //Modify the states of the Modal selected products if there is any quantity change
      if (modalSelectedProductsMap.has(product.id)) {
        setModalSelectedProductsMap((prevModalSelectedProductsMap) => {
          const updatedModalSelectedProductsMap = new Map(
            prevModalSelectedProductsMap
          );

          const existingModalSelectedProduct =
            updatedModalSelectedProductsMap.get(product.id);

          if (existingModalSelectedProduct) {
            updatedModalSelectedProductsMap.set(product.id, {
              ...existingModalSelectedProduct,
              quantity: quantity,
              totalMRP: totalMRP,
              netSellingPrice: netSellingPrice,
              totalDiscount: totalDiscount,
            });
          }

          const updatedModalSelectedProducts = Array.from(
            updatedModalSelectedProductsMap.values()
          );
          setModalSelectedProducts(updatedModalSelectedProducts);

          return updatedModalSelectedProductsMap;
        });
      }
    };

    const handleClickLoadMore = (
      event: React.MouseEvent<HTMLAnchorElement>,
      product: userSelectedProducts,
      parentProductID: number
    ) => {
      console.log("Within handleClickLoadMore");
      console.log("product:", product);
      console.log("parentProductID:", parentProductID);
      event.preventDefault();
      setLoadMoreClicked(true);
      setSelectedProduct(product);
      setSelectedParentProductID(parentProductID);
      // Reset modal states
      setModalSelectedProductsMap(new Map());
      setModalSelectedProducts([]);

      //Get the main product as well as its child of the main product from products state using parent product id.
      const modalParentChild = products.find((p) => p.id === parentProductID);

      if (modalParentChild) {
        setModalParentChild(modalParentChild);
      }

      // const updatedModalParentChild = products[index];
      // setModalParentChild(updatedModalParentChild)

      //Prepare products for modal display, parent product followed by child products.
      const modalProductsForDisplay = [
        product,
        ...(modalParentChild?.children || []),
      ].filter((item) => item !== undefined); // Filter out undefined values

      // Update modal display products state
      setModalDisplayProducts(modalProductsForDisplay);

      console.log("Load more clicked products, modalDisplayProducts:", modalDisplayProducts);
    };

    function handleDeleteProduct(productID: number): void {
      console.log("WITHIN handleDeleteProduct, PRODUCT ID", productID);

      setDisplayProducts((prevDisplayProducts) => {
        const updatedDisplayProducts = prevDisplayProducts.filter(
          (product) => product.id !== productID
        );
        return updatedDisplayProducts;
      });

      setUserSelectedProductsMap((prevUserSelectedProductsMap) => {
        const updatedUserSelectedProductsMap = new Map(
          prevUserSelectedProductsMap
        );

        if (updatedUserSelectedProductsMap.has(productID)) {
          updatedUserSelectedProductsMap.delete(productID);
        }

        const updatedUserSelectedProducts = Array.from(
          updatedUserSelectedProductsMap.values()
        );
        setUserSelectedProducts(updatedUserSelectedProducts);
        return updatedUserSelectedProductsMap;
      });
    }

    // const isProductChecked = (!showModal && userSelectedProductsMap.has(product.id)) ||
    // (showModal && modalSelectedProductsMap.has(product.id)) ||
    // (!showModal && Array.from(modalSelectedProductsMap.keys()).some(productID =>
    //    userSelectedProductsMap.has(productID)
    // ))

    return (
      <tr className="table table-striped" key={product.id}>
        <td className="table-data-font">
          <input
            type="checkbox"
            name="productSelect"
            value={product.id}
            onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
              handleCheckBoxChange(product, event.target.checked)
            }
            // checked={isProductChecked
            //   // (!showModal && userSelectedProductsMap.has(product.id)) ||
            //   // (showModal && modalSelectedProductsMap.has(product.id)) ||
            //   // (!showModal && userSelectedProductsMap.has(modalSelectedProductsMap.))
            // }
            checked={(!showModal && userSelectedProductsMap.has(product.id)) ||
            (showModal && modalSelectedProductsMap.has(product.id))}
            disabled={isConfirmedByUser}
          />
        </td>
        <td className="table-data-font">{product.name}</td>
        <td className="table-data-font">{product.brand.name}</td>
        <td className="table-data-font">{product.weight}</td>
        {!showModal && (
            <td className="table-data-font">
              <select
                className="form-select small-dropdown table-data-font"
                value={product.quantity}
                onChange={(event) => handleQuantityChange(product, event)}
                disabled={isConfirmedByUser}
              >
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
                <option value="6">6</option>
                <option value="7">7</option>
                <option value="8">8</option>
                <option value="9">9</option>
                <option value="10">10</option>
              </select>
            </td>
        )} 
        <td className="table-data-font">
          Rs. {product.pricing.mrp.toFixed(2)}
        </td>
        {/* <td className="table-data-font">{1 * product.pricing.mrp}</td> */}
        <td className="table-data-font">{product.pricing.discount}</td>
        {/* <td className="table-data-font">1 * {product.pricing.discount}</td> */}
        <td className="table-data-font">
          Rs. {product.pricing.selling_price.toFixed(2)}
        </td>
        {!showModal && (
          <>
            <td className="table-data-font">
              Rs. {product.totalMRP?.toFixed(2)}
            </td>
            <td className="table-data-font">
              Rs. {product.totalDiscount?.toFixed(2)}
            </td>
            <td className="table-data-font">
              Rs. {product.netSellingPrice?.toFixed(2)}
            </td>
          </>
        )}

        <td className="table-data-font">
          {!showModal ? (
            product.keep_selected === "Y" ? (
              isConfirmedByUser ? (
                <span style={{ color: "grey", cursor: "not-allowed" }}>
                  Load More
                </span>
              ) : (
                <a
                  href="#"
                  onClick={(event) =>
                    handleClickLoadMore(event, product, product.id)
                  }
                >
                  Load More
                </a>
              )
            ) : (
              <span>Other Option</span>
            )
          ) : product.keep_selected === "Y" ? (
            <span style={{ color: "#0d6efd" }}>Recommended</span>
          ) : (
            <span>Other Option</span>
          )}
        </td>
        {!showModal && (
          <td
            className={`table-cell ${
              isConfirmedByUser ? "table-cell-no-hover" : ""
            }`}
          >
            <button
              // className="btn-icon-inline btn-light rounded-0"
              className="btn btn-icon-inline btn-light btn-sm"
              type="button"
              onClick={() => handleDeleteProduct(product.id)}
              disabled={isConfirmedByUser}
            >
              <FontAwesomeIcon
                icon={faTrashCan}
                style={{
                  padding: "0",
                  margin: "0",
                  color: "#635656",
                  opacity: 1,
                }}
              />
            </button>
            {/* faTrashCan, faTrashRestore, faTrashRestoreAlt */}
          </td>
        )}
      </tr>
    );
  }

  // ProductModal is a Custom Modal Component
  function ProductModal({
    parentProductID,
    product,
    onClose,
  }: ProductModalProps) {
    console.log("Within showProductModal, parent product ID:", parentProductID);
    console.log("product:", product);
    if (!product) return null;

    function handleSaveModalChanges(
      event: MouseEvent<HTMLButtonElement>
    ): void {
      console.log("Within handleSaveModalChanges");
      // console.log("**************************************************************************")
      // console.log("Before update modalDisplayProducts:", modalDisplayProducts)
      // console.log("Before update modalSelectedProductsMap:", modalSelectedProductsMap)
      // console.log("**************************************************************************")

      // Initialize updatedModalSelectedProducts and updatedModalSelectedProductsMap
      // let updatedModalSelectedProducts: userSelectedProducts[] = [];
      // let updatedModalSelectedProductsMap = new Map<number, userSelectedProducts>();

      //Update the latest quantities in modalDisplayProducts array and modalSelectedProductsMap from modalDisplayProducts
      setModalSelectedProductsMap((prevModalSelectedProductsMap) => {
        const updatedModalSelectedProductsMap = new Map(
          prevModalSelectedProductsMap
        );

        modalDisplayProducts.forEach((p) => {
          if (updatedModalSelectedProductsMap.has(p.id)) {
            const existingModalSelectedProduct =
              updatedModalSelectedProductsMap.get(p.id);

            if (existingModalSelectedProduct) {
              const quantity = p.quantity || 1;
              const totalMRP =
                quantity * existingModalSelectedProduct.pricing.mrp;
              const netSellingPrice =
                quantity * existingModalSelectedProduct.pricing.selling_price;
              const totalDiscount = totalMRP - netSellingPrice;

              updatedModalSelectedProductsMap.set(p.id, {
                ...existingModalSelectedProduct,
                quantity: quantity,
                totalMRP: totalMRP,
                netSellingPrice: netSellingPrice,
                totalDiscount: totalDiscount,
              });
            }
          }
        });

        const updatedModalSelectedProducts = Array.from(
          updatedModalSelectedProductsMap.values()
        );
        setModalSelectedProducts(updatedModalSelectedProducts);

        // console.log("updatedModalSelectedProducts:", updatedModalSelectedProducts);
        // console.log("updatedModalSelectedProductsMap:", updatedModalSelectedProductsMap)
        // console.log("**************************************************************************")

        modifyMainPageProductDetails(
          updatedModalSelectedProducts,
          updatedModalSelectedProductsMap,
          parentProductID
        );

        return updatedModalSelectedProductsMap;
      });

      // console.log("After update modalSelectedProducts:", modalSelectedProducts)
      // console.log("After update modalSelectedProductsMap:", modalSelectedProductsMap)
      // console.log("**************************************************************************")
    }

    function modifyMainPageProductDetails(
      updatedModalSelectedProducts: userSelectedProducts[],
      updatedModalSelectedProductsMap: Map<number, userSelectedProducts>,
      parentProductID: number
    ) {
      console.log("WITHIN modifyMainPageProductDetails")
      //Update the displayProducts in the main create order web page to replace the parent product with
      //the products chosen from from Modal.
      setDisplayProducts((prevDisplayProducts) => {
        const updatedDisplayProducts = [...prevDisplayProducts];

        const parentProduct = updatedDisplayProducts.find(
          (product) => product.id === parentProductID
        );

        if (!parentProduct) {
          console.error("Parent product not found.");
          return prevDisplayProducts;
        }
        const parentProductIndex =
          updatedDisplayProducts.indexOf(parentProduct);
        updatedDisplayProducts.splice(
          parentProductIndex,
          1,
          ...updatedModalSelectedProducts
        );

        return updatedDisplayProducts;
      });

      //Remove the parent product details from userSelectedProductsMap if the parent product ID is present in it.
      setUserSelectedProductsMap((prevUserSelectedProductsMap) => {
        const updatedUserSelectedProductsMap = new Map(
          prevUserSelectedProductsMap
        );

        //After the user has selected the optional products from the Modal, remove the recommended or
        //parent product from userSelectedProductsMap and add the optional products chosen from
        //Modal. updatedModalSelectedProductsMap will contain the products that were chosen from the
        //Modal.
        if (updatedUserSelectedProductsMap.has(parentProductID)) {
          updatedUserSelectedProductsMap.delete(parentProductID);
        }

        updatedModalSelectedProductsMap.forEach((productValue, productKey) => {
          updatedUserSelectedProductsMap.set(productKey, productValue)
        })

        const updatedUserSelectedProducts = Array.from(
          updatedUserSelectedProductsMap.values()
        );
        setUserSelectedProducts(updatedUserSelectedProducts);

        return updatedUserSelectedProductsMap;
      });
    }

    return (
      <div
        className="modal show d-block"
        tabIndex={-1}
        style={{
          backgroundColor: "rgba(0,0,0,0.5)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div
          className="modal-dialog modal-dialog-scrollable modal-xl"
          style={{ width: "90%" }}
        >
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">More Options</h5>
              <button
                type="button"
                className="btn-close"
                aria-label="Close"
                onClick={onClose}
              ></button>
            </div>
            <div className="modal-body">
              <div className="table-responsive">
                {/* <table className="table table-secondary table-striped table-bordered"> */}
                <table className="table table-secondary table-bordered table-sm w-100 text-xsmall table-hover">
                  <TableHeader lastColumnName={"Options"} showModal={true} />
                  <tbody>
                    {product.map((modalProduct, modalIndex) => (
                      <TableRow
                        key={modalProduct.id}
                        product={modalProduct}
                        showModal={true}
                        index={modalIndex}
                        parentOrChild={modalProduct.keep_selected === "N" ? "child" : "parent"}
                      />
                    ))}
                  </tbody>
                </table>
              </div>
              {/* Add other product details here */}
            </div>
            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={onClose}
              >
                Close
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleSaveModalChanges}
              >
                Save changes
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  function EndCard() {
    const [endCardGrandTotals, setEndCardGrandTotals] = useState({
      GrandTotalMRP: 0.0,
      GrandTotalSellingPrice: 0.0,
      GrandTotalDiscount: 0.0,
    });

    useEffect(() => {
      let GrandTotalMRP = 0.0;
      let GrandTotalSellingPrice = 0.0;
      let GrandTotalDiscount = 0.0;

      userSelectedProducts.forEach((product) => {
        GrandTotalMRP += product.totalMRP || 0;
        GrandTotalSellingPrice += product.netSellingPrice || 0;
        GrandTotalDiscount += product.totalDiscount || 0;
      });

      setEndCardGrandTotals({
        GrandTotalMRP,
        GrandTotalSellingPrice,
        GrandTotalDiscount,
      });
    }, [userSelectedProducts]);

    return (
      <>
        <div className="row justify-content-end">
          <div className="col-4">
            <div className="card p-3">
              <h5 className="card-title text-decoration-underline">
                Order Summary
              </h5>
              <p className="card-text">
                Total Price MRP: Rs.{" "}
                {endCardGrandTotals.GrandTotalMRP.toFixed(2)}
              </p>
              <p className="card-text">
                Total Discount: Rs.{" "}
                {endCardGrandTotals.GrandTotalDiscount.toFixed(2)}
              </p>
              <p className="card-text text-success fw-bold">
                Net Amount To Be Paid: Rs.{" "}
                {endCardGrandTotals.GrandTotalSellingPrice.toFixed(2)}
              </p>
            </div>
          </div>
        </div>
      </>
    );
  }

  document.title = "AndrewBot - Create Order";

  //Reset to initial state when the create order page 1st loaded.
  function handleReset(event: MouseEvent<HTMLButtonElement>): void {
    if (orderResponse) {
      setOrderResponse({ ...orderResponse });
    }
  }

  //Final Order Confirmation Processing
  //***********************************/
  function confirmOrder(event: MouseEvent<HTMLButtonElement>): void {
    const isConfirmed = window.confirm(
      "Are you sure you want to confirm the order ?"
    );

    if (isConfirmed) {
      console.log("Order Confirmed!!!");
      setIsConfirmedByUser(true);

      // Create a copy of userSelectedProductsMap to update
      const updatedUserSelectedProductsMap = new Map(userSelectedProductsMap);
      console.log(
        "updatedUserSelectedProductsMap:",
        updatedUserSelectedProductsMap
      );

      // Loop through displayProducts to get the latest quantities
      displayProducts.forEach((product) => {
        if (updatedUserSelectedProductsMap.has(product.id)) {
          console.log("Hii");
          const existingProduct = updatedUserSelectedProductsMap.get(
            product.id
          );
          if (existingProduct) {
            const quantity = product.quantity || 1;
            const totalMRP = quantity * product.pricing.mrp;
            const netSellingPrice = quantity * product.pricing.selling_price;
            const totalDiscount = totalMRP - netSellingPrice;

            existingProduct.quantity = quantity;
            existingProduct.totalMRP = totalMRP;
            existingProduct.netSellingPrice = netSellingPrice;
            existingProduct.totalDiscount = totalDiscount;

            updatedUserSelectedProductsMap.set(product.id, existingProduct);
          }
        }
      });

      // Update the state with the modified products
      setUserSelectedProductsMap(updatedUserSelectedProductsMap);

      const updatedUserSelectedProducts = Array.from(
        updatedUserSelectedProductsMap.values()
      );
      setUserSelectedProducts(updatedUserSelectedProducts);

      console.log("Final order:", userSelectedProducts);
      console.log("Final order1:", updatedUserSelectedProducts);

      //Format the request body before making the API call
      const formattedDataForOrderConfirmationAPIcall =
        formatDataForOrderConfirmationAPIcall(updatedUserSelectedProducts);
      //
      //Make backend OrderManagementAPI call with the selected product details

      // Call the API function
      orderConfirmationAPIcall(formattedDataForOrderConfirmationAPIcall);
    } else {
      console.log("Order cancelled!!!");
    }
  }

  function formatDataForOrderConfirmationAPIcall(
    updatedUserSelectedProducts: userSelectedProducts[]
  ) {
    let totalAmountMRP = 0.0;
    let totalDiscountAmount = 0.0;
    let netTotalAmount = 0.0;

    updatedUserSelectedProducts.forEach((product) => {
      totalAmountMRP += product.totalMRP || 0.0;
      totalDiscountAmount += product.totalDiscount || 0.0;
      netTotalAmount += product.netSellingPrice || 0.0;
    });

    // Get current and future dates and format them into "DD-MM-YYYY HH:MM:SEC"
    const currentDate = new Date();
    const currentTimestamp = getTimestamp(currentDate);
    console.log("currentTimestamp", currentTimestamp);

    const futureDate = new Date(currentDate);
    futureDate.setDate(currentDate.getDate() + 7);
    const futureTimestamp = getTimestamp(futureDate);
    console.log("futureTimestamp", futureTimestamp);

    // Set up a default test address
    const testAddress: Address = {
      houseNumber: "A102",
      buildingName: "ABC Building",
      street: "XYZ Street",
      addressLine1: "Test Address Line1",
      addressLine2: "Test Address Line2",
      addressLine3: "Test Address Line3",
      city: "Test City",
      state: "Test State",
      pincode: 123456,
      landMark: "Test Landmark",
      country: "India",
    };

    //Assign the data for API call
    const formattedDataForOrderConfirmationAPIcall: createOrderAPIcallInterface =
      {
        userID: "ghoshanirban", //Default user
        products: updatedUserSelectedProducts,
        orderConfirmedByUser: "Y",
        orderCreatedDate: currentTimestamp,
        orderFulfilled: "N",
        orderFulfillmentDate: "00-00-0000 00:00:00", //Assign a NULL Date
        totalAmountMRP: totalAmountMRP,
        totalDiscountAmount: totalDiscountAmount,
        netTotalAmount: netTotalAmount,
        billingAddress: testAddress,
        shippingAddress: testAddress,
        paymentMethod: "credit card", //Default payment mode
        estimatedOrderFulfillmentDate: futureTimestamp,
      };

    return formattedDataForOrderConfirmationAPIcall;
  }

  function getTimestamp(date: {
    getDate: () => any;
    getMonth: () => number;
    getFullYear: () => any;
    getHours: () => any;
    getMinutes: () => any;
    getSeconds: () => any;
  }) {
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");
    const timestamp = `${day}-${month}-${year} ${hours}:${minutes}:${seconds}`;
    return timestamp;
  }

  async function orderConfirmationAPIcall(
    formattedDataForOrderConfirmationAPIcall: createOrderAPIcallInterface
  ) {
    console.log("within orderConfirmationAPIcall");
    setLoading(true);

    const requestBody = formattedDataForOrderConfirmationAPIcall;

    try {
      const APIResponse = await axios.post(`${API_URL}/orders/create`, {
        UserConfirmedProducts: requestBody,
      });

      if (APIResponse.status === 200) {
        console.log("Order Created Successfully!!!");
        console.log("API Response:", APIResponse.data);
        const orderID = APIResponse.data.orderID;

        if (orderID) {
          console.log("YOUR ORDER ID IS: ", orderID);
          setOrderID(orderID);
          localStorage.clear()
          localStorage.setItem("orderID", JSON.stringify(orderID));
        } else {
          console.log("INVALID ORDER ID GENERATED: ", orderID);
        }
      } else {
        console.log(
          "!!!Bad Response from OrderManagementAPI call for Create Order!!!"
        );
        console.log("BAD RESPONSE STATUS CODE:", APIResponse.status);
      }
    } catch (error) {
      console.log("Error creating order during axios POST call:", error);
    } finally {
      setLoading(false);
      console.log("Finished Order Creation Process!!!");
    }
  }

  // console.log("products:", products)
  return (
    <>
      <nav className="navbar" style={{ backgroundColor: "#e3f2fd" }}>
        <div className="container-fluid">
          <div className="row w-100">
            <div className="col-6">
              <span className="navbar-brand mb-0 h1">
                AndrewBot - Create Order
              </span>
            </div>
            <div className="col-6 text-end pe-5">
              <span className="navbar-text font-monospace fw-semibold">
                User ID: ghoshanirban
                <br />
                Date: {currentDate}
              </span>
            </div>
          </div>
        </div>
      </nav>

      <div className="container mt-4">
        <p className="fs-5 fw-semibold text-center text-decoration-underline pt-3">
          Here You Can Edit / Modify Your Requested Order
        </p>

        {/* Spinner showing Loading status*/}
        {loading ? (
          <div className="d-flex justify-content-center">
            <div className="spinner-border text-secondary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        ) : (
          <>
            <div className="table-responsive">
              <table
                className={`table table-secondary table-bordered table-sm w-auto text-xsmall ${
                  isConfirmedByUser ? "" : "table-hover"
                }`}
              >
                <TableHeader
                  lastColumnName={"More Options"}
                  showModal={false}
                />

                <tbody>
                  {displayProducts.map((product, index) => (
                    <TableRow
                      key={product.id}
                      product={product}
                      showModal={false}
                      index={index}
                      parentOrChild={product.keep_selected === "N" ? "child" : "parent"}
                    />
                  ))}
                </tbody>
              </table>

              {selectedProduct &&
                loadMoreClicked &&
                showModal &&
                modalDisplayProducts.length > 0 &&
                selectedParentProductID !== undefined && (
                  <ProductModal
                    parentProductID={selectedParentProductID}
                    product={modalDisplayProducts}
                    onClose={() => {
                      setShowModal(false);
                      setLoadMoreClicked(false);
                    }}
                  />
                )}
            </div>
            {/* END CARD FOR GRAND TOTALS */}

            <EndCard />

            {/* END CARD END */}

            <br />

            {isConfirmedByUser && orderID && (
              <div
                className={`modal ${showModalOrderID ? "show" : ""}`}
                tabIndex={-1}
                style={{ display: showModalOrderID ? "block" : "none" }}
              >
                <div className="modal-dialog modal-dialog-centered">
                  <div className="modal-content">
                    <div
                      className="modal-header"
                      style={{ backgroundColor: "#68b18f", color: "white" }}
                    >
                      <h5 className="modal-title">
                        Congratulations!!! Your Order Has Been Successfully
                        Generated.
                      </h5>
                      <button
                        type="button"
                        className="btn-close"
                        data-bs-dismiss="modal"
                        onClick={handleCloseModalOrderID}
                        aria-label="Close"
                        style={{
                          position: "absolute",
                          top: "12px",
                          right: "12px",
                        }}
                      ></button>
                    </div>
                    <div
                      className="modal-body"
                      style={{ backgroundColor: "#c2ddd1", color: "#1c4130" }}
                    >
                      <h6>Please Note Down Your Order ID: {orderID}</h6>
                      <p>
                        This Window Can Be Closed Now. Please Go To The Bot
                        Window For More Actions.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="d-grid gap-2 d-md-flex justify-content-center">
              <button
                className="btn btn-secondary me-md-2 btn-lg"
                type="reset"
                value="Reset"
                onClick={handleReset}
                disabled={isConfirmedByUser}
              >
                Reset
              </button>
              <button
                className="btn btn-primary btn-lg"
                type="button"
                onClick={confirmOrder}
                disabled={isConfirmedByUser}
              >
                Confirm
              </button>
            </div>
          </>
        )}
      </div>
    </>
  );
}
