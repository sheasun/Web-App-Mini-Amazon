import Dialog from '@material-ui/core/Dialog';
import Cookies from 'js-cookie';
import { useState } from 'react';
 
export default function AddCartDialog({_open, _close, _onClose, _id, _itemName, _maxCount}){

  // "placeOrder" or "purchaseMore"
  const[buttonAction, setButtonAction] = useState('placeOrder');

  const addToCart = async event => {
    event.preventDefault();
    const token = Cookies.get('token');

    console.log(buttonAction);

    let formData = new FormData();
    formData.append("stockId", _id);
    formData.append("amount", event.target.amount.value);

    if(buttonAction  == 'placeOrder'){
      const result =  await fetch(`${process.env.httpHost}/cart`, {
        method: "post",
        headers: {
          "x-access-tokens": token
        },
        body: formData
      });
      const status = result.status;
      const response = await result.json();
      console.log(response["message"]);
      window.location.reload(false);
    }
    else{
      const result =  await fetch(`${process.env.httpHost}/purchaseMore`, {
        method: "post",
        headers: {
          "x-access-tokens": token
        },
        body: formData
      });
      const status = result.status;
      const response = await result.json();
      console.log(response["message"]);
      window.location.reload(false);
    }
  }

  const purchaseMore = async () => {
    const token = Cookies.get('token');
    
    let formData = new FormData();
    formData.append("stockId", _id);

    const result =  await fetch(`${process.env.httpHost}/purchaseMore`, {
      method: "post",
      headers: {
        "x-access-tokens": token
      },
      body: formData
    });
    const status = result.status;
    const response = await result.json();
    console.log(response["message"]);
    window.location.reload(false);
  }

  return(
    <Dialog open={_open} onClose={_onClose}>
    <div className='p-2 space-y-2'>
      <div className='text-center py-2'>
        <p className='font-bold'>Add to Shopping Cart</p>
      </div>
      <div className='flex flex-row justify-center text-center p-2 space-x-2'>
        <p>{_itemName}</p>
        <form id='form' onSubmit={addToCart}>
          <input name="amount" type="number" defaultValue={1} min={1} max={parseInt(_maxCount)}/>
        </form>
      </div>
      <div className='text-center'>
        <button form='form' className='md_btn' onClick={() => setButtonAction("placeOrder")}>Put In Cart</button>
      </div>
      <div className='text-center'>
        <button className='md_btn' onClick={() => purchaseMore()}>Request Extra 10</button>
      </div>
      <div className='text-center'>
        <button className='btn' onClick={_close}>Close</button>
      </div>
    </div>
  </Dialog>
  )
}