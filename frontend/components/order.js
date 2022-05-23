import { useRouter } from "next/router";

export default function Order({id, status, truckId, whId, note}){

  const router = useRouter();

  const getDeliveryDetails = () => {
    router.push({
        pathname: '/deliveryDetails',
        query: { order_id: id }
    });
  }

  return(
    <div 
      className={`w-6/12 mx-auto p-2 ${id%2 == 0 ? 'bg-blue-400': 'bg-blue-200'} hover:cursor-pointer`}
      onClick={()=>getDeliveryDetails()}
    >
      <div className={"grid grid-flow-col gap-4 grid-cols-5  p-2 text-center mx-auto"}>
        <div className="col-span-1 font-bold flex flex-row">
          Order ID: <p className="font-normal">{id}</p>
        </div>
        <div className="col-span-2 font-bold flex flex-row">
          Status: <p className="italic font-bold">{status}</p>
        </div>
        <div className="col-span-1 font-bold flex flex-row">
          Truck ID: {truckId}
        </div>
        <div className="col-span-1 font-bold flex flex-row">
          Warehouse ID: {whId}
        </div>
      
      </div>
      <div className="flex flex-col text-center font-serif">
          {"Notes: " + note}
        </div>
    </div>
  );
}