import Header from "../components/header";
import StockItem from "../components/stockItem";
import {CurrencyDollarIcon} from '@heroicons/react/outline';
import Cookies from 'js-cookie';
import WarningDialog from '../components/warningDialog';
import { useState } from "react";

export default function Cart({stocks}){

  console.log(stocks);

  const [warningDialogOpen, setWarningDialogOpen] = useState(false);

  const placeOrder = async () => {
    if(Object.keys(stocks['product']).length === 0){
      setWarningDialogOpen(true);
      return;
    }

    const token = Cookies.get('token');

    const orderId = stocks['orderId'];
    let formData = new FormData();
    formData.append("orderId", orderId);

    const result =  await fetch(`${process.env.httpHost}/placeOrder`, {
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
    <div className='flex flex-col justify-center space-y-2 items-center'>
      <WarningDialog 
        _open={warningDialogOpen} 
        _close={() => setWarningDialogOpen(false)}
        _onClose={() => setWarningDialogOpen(false)}
        _message="Your shopping cart is empty"
      />
      <Header title="My Cart"/>     
      {
        Object.keys(stocks['product']).length === 0 ? 
        <p>Your cart is empty</p> :
        <div className="flex flex-col w-full space-y-2 mx-auto">
        {
          stocks['product'].map((stock, index) => 
            <StockItem key={index} id={index} name={stock['name']} availability={stock['count']}/>
          )
        }
        </div>
      }
      <div 
        className="flex flex-row p-2 rounded-xl items-center my-auto bg-red-200 
          hover:cursor-pointer hover:bg-red-400"
        onClick={() => placeOrder()}
      >
        <p className="font-bold">Checkout</p>
        <CurrencyDollarIcon className="h-8"/>
      </div>
    </div>
  );
}

export async function getServerSideProps({req, rep}){
  const token = req.cookies.token || null;

  const result =  await fetch(`${process.env.httpHost}/cart`, {
    method: "get",
    headers: {
      "x-access-tokens": token
    }
  });

  if(result.status != 200){
    return {
      redirect: {
        destination: "/login",
        permanent: false,
      }
    }
  }
  
  const stocks = await result.json();
  return {
    props: {
      stocks: stocks,
    }
  }
}