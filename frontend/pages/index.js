import { useState } from 'react';
import AddCartDialog from '../components/addCartDialog';
import Header from '../components/header';
import StockItem from '../components/stockItem';
import Cookies from 'js-cookie';

export default function Home({stocks}) {

  console.log(stocks);

  const [searchIndex, setSearchIndex] = useState('');
  const [addCartDialogOpen, setAddCartDialogOpen] = useState(false);
  const [stockId, setStockId] = useState(-1);
  const [cartItem, setCartItem] = useState(null);
  const [maxCount, setMaxCount] = useState(0);

  const prepareAddCartDialog = (stock) => {
    setStockId(stock['id']);
    setCartItem(stock['name']);
    setMaxCount(stock['count']);
    setAddCartDialogOpen(true);
  }

  const purchaseNewItem = async event => {
    event.preventDefault();

    const token = Cookies.get('token');

    let formData = new FormData();
    formData.append("description", event.target.description.value);
    formData.append("count", event.target.count.value);

    const result =  await fetch(`${process.env.httpHost}/purchaseMore/new`, {
      method: "post",
      body: formData,
      headers: {
        "x-access-tokens": token
      }
    });
    const status = result.status;
    const response = await result.json();
    console.log(response);
    window.location.reload(false);
  }

  return(
    <div className='flex flex-col space-y-2 items-center'>
      <AddCartDialog 
        _open={addCartDialogOpen} 
        _close={() => setAddCartDialogOpen(false)} 
        _id={stockId} 
        _itemName={cartItem}
        _maxCount={maxCount}
      />
      <Header/>

      <div className='flex flex-col items-center space-y-2 p-2'>
        <p className='font-bold'>Request for purchase of products not listed below</p>
        <form id='purchanseNewForm' className='table' onSubmit={purchaseNewItem}>
          <p className='table-row space-x-2'>
            <label className='table-cell' htmlFor='description'>Description: </label>
            <input className='table-cell my-1 border-2' name='description' type='text' required></input>
          </p>
          <p className='table-row space-x-2'>
            <label className='table-cell' htmlFor='count'>Count: </label>
            <input className='table-cell my-1 border-2' name='count' type='number' defaultValue={1} min={1} required></input>
          </p>
        </form>
        <button className='btn' form='purchanseNewForm'>
          Confirm
        </button>
      </div>

      <div className="grid grid-flow-col gap-4 grid-cols-4 w-6/12 bg-gray-200 rounded-lg p-2 text-center">
        <div className="col-span-1 font-serif">
          Name
        </div>
        <div className="col-span-1 font-serif">
          <input 
            type='text' 
            onChange={(event) => setSearchIndex(event.target.value)}
            className='border-2 border-blue-200'
          />
        </div>
        <div className="col-span-1 font-serif">
          Price
        </div>
        <div className="col-span-2 font-serif">
          Availability
        </div>
      </div>

      {
        stocks['product'].filter(stock => stock['name'].toLowerCase().includes(searchIndex.toLowerCase())).map((stock, index) => 
          <StockItem 
            key={index}
            id={index} 
            name={stock['name']} 
            availability={stock['count']} 
            _onClick={() => prepareAddCartDialog(stock)}/>
          )
      }

    </div>
  )
}

export async function getServerSideProps({req, rep}){
  const token = req.cookies.token || null;

  const result =  await fetch(`${process.env.httpHost}/stocks`, {
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