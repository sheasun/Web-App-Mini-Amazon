import { useState } from 'react';
import Header from '../components/header';
import Order from '../components/order';

export default function Deliveries({deliveries}){

  console.log(deliveries);

  const [packageIdIndex, setPackageIdIndex] = useState('');

  // const updatePackageIdIndex = (event) => {
  //   console.log(event.target.value);
  //   console.log(event.target.value === undefined);
  //   setPackageIdIndex(event.target.value);
  // }

  return(
    <div className='flex flex-col space-y-2 items-center'>
      <Header title='Deliveries'/>

      <div className="grid grid-flow-col gap-4 grid-cols-4 w-4/12 bg-gray-200 rounded-lg p-2 text-center">
        <div className="col-span-1 font-serif">
          Order ID
        </div>
        <div className="col-span-1 font-serif">
          <input 
            type='number' 
            min={1}
            onChange = {(event) => {setPackageIdIndex(event.target.value)}}
            // onChange = {updatePackageIdIndex}
            className='border-2 border-blue-200'
          />
        </div>
      </div>

      <div className="flex flex-col w-full space-y-2 mx-auto">
        {
          deliveries['orders'].filter(order => packageIdIndex !== '' ? parseInt(order['id']) === parseInt(packageIdIndex) : order).map((order, index) =>
            <Order 
              key={index}
              id={order['id']} 
              status={order['status']} 
              truckId={order['truck_id']} 
              whId={order['wh_id']} 
              note={order['note']}/>
          )
        }
      </div>
    </div>
  );
}

export async function getServerSideProps({req, rep}){
  const token = req.cookies.token || null;

  const result =  await fetch(`${process.env.httpHost}/deliveries`, {
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
  
  const deliveries = await result.json();
  return {
    props: {
      deliveries: deliveries,
    }
  }
}