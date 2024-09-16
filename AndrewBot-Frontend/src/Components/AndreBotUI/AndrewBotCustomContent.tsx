import React, { useState } from "react";
import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";
import "./AndrewBotCustom.css";
import { Message, Button } from "@chatscope/chat-ui-kit-react";

interface AndrewBotCustomContentProps {
  onChoiceSelected: (chosenAction: string) => void;
}

export default function AndrewBotCustomContent({onChoiceSelected,}: AndrewBotCustomContentProps) {
  //State to manage which buttons are disabled
  const [disabledButtons, setDisabledButtons] = useState({
    createOrder: false,
    viewOrder: false,
    exit: false
  });
  
  // Function to handle button clicks
  const handleButtonClick = (action: string) => {
    onChoiceSelected(action);

    // Disable other buttons based on the action
    if (action === "Create Order") {
      setDisabledButtons({ createOrder: true, viewOrder: true, exit: true });
    } else if (action === "View Order") {
      setDisabledButtons({ createOrder: true, viewOrder: true, exit: true });
    } else if (action === "Exit") {
      setDisabledButtons({ createOrder: true, viewOrder: true, exit: true });
    }
  };
  

  return (
    <Message.CustomContent>
      <div
        style={{
          display: "flex",
          justifyContent: "space-around",
        }}
      >
        <Button
          className="cs-button-AndrewBot-options"
          onClick={() => handleButtonClick("Create Order")}
          disabled={disabledButtons.createOrder}
        >
          Create Order
        </Button>
        <Button
          className="cs-button-AndrewBot-options"
          onClick={() => handleButtonClick("View Order")}
          disabled={disabledButtons.viewOrder}
        >
          View Order
        </Button>
        <Button
          className="cs-button-AndrewBot-options"
          onClick={() => handleButtonClick("Exit")}
          disabled={disabledButtons.exit}
        >
          Exit
        </Button>
      </div>
    </Message.CustomContent>
  );
}
