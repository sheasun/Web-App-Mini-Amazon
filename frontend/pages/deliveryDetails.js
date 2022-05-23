import StockItem from '../components/stockItem';
import Header from '../components/header';

export default function DeliveryDetails({delivery}){
  
  console.log(delivery);

  return(
    <div className='flex flex-col justify-center space-y-2 items-center'>
      <Header title='Detail'/>
      {
        delivery['product'].map((item, index) => 
          <StockItem key={index} id={index} name={item['name']} availability={item['count']}/>
        )
      }
    </div>
  );
}

export async function getServerSideProps({req, rep, query}){
  const token = req.cookies.token || null;

  const result =  await fetch(`${process.env.httpHost}/delivery?order_id=${query.order_id}`, {
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
  
  const delivery = await result.json();
  return {
    props: {
      delivery: delivery,
    }
  }
}