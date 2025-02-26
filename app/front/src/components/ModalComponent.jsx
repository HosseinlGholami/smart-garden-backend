import React from "react";
import { Button, Modal, ModalBody, ModalFooter, ModalHeader } from "reactstrap";

const ModalComponent = ({ isOpen, message, toggle, custom }) => {
  return (
    <Modal isOpen={isOpen} toggle={toggle}>
      <ModalHeader>Result:</ModalHeader>
      <ModalBody>{message}</ModalBody>
      <ModalFooter>
        {custom && <div>{custom}</div>}
        <Button color="secondary" onClick={toggle}>
          Close
        </Button>

      </ModalFooter>
    </Modal>
  );
};

export default ModalComponent;
