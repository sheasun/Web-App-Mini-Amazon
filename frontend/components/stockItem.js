export default function StockItem({id, name="asdfas", price="n/a", availability="n/a", _onClick}){
  return(
    <div className={
      `grid grid-flow-col gap-4 grid-cols-4 w-6/12 p-2 text-center mx-auto
      ${id%2 == 0 ? 'bg-blue-400': 'bg-blue-200'} hover:cursor-pointer`
      }
      onClick={_onClick}
    >
      <div className="col-span-2 font-bold">
        {name}
      </div>
      <div className="col-span-1">
        {price}
      </div>
      <div className="col-span-2">
        {availability}
      </div>
    </div>
  );
}