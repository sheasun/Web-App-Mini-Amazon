import Header from "../components/header";
import Cookies from 'js-cookie';
import { useState } from "react";
import WarningDialog from "../components/warningDialog";

export default function UpdateUser({body}){

  console.log(body);

  const userInfo = body['userInfo'];

  const [warningDialogOpen, setWarningDialogOpen] = useState(false);
  const [warningMessage, setWarningMessage] = useState(null);
  
  const setErrorMessageAndOpenDialog = (warningMessage) => {
    setWarningMessage(warningMessage);
    setWarningDialogOpen(true);
    console.log(warningMessage);
  }

  const resetErrorMessageAndCloseDialog = () => {
    setWarningMessage(null);
    setWarningDialogOpen(false);
  }

  const updateUserInfo = async(event) => {
    event.preventDefault();
    const token = Cookies.get('token');

    const email = event.target.email.value;
    const name = event.target.name.value;
    const upsName = event.target.upsName.value;
    const password = event.target.password.value;
    const confirmedPassword = event.target.confirm_password.value;
    const locationX = event.target.location_x.value;
    const locationY = event.target.location_y.value;

    if(password != confirmedPassword){
      const warningMessage = "password not the same";
      setErrorMessageAndOpenDialog(warningMessage);
      return;
    }

    let formData = new FormData();
    formData.append("email", email);
    formData.append("name", name);
    formData.append("upsName", upsName);
    formData.append("password", password);
    formData.append("location_x", locationX);
    formData.append("location_y", locationY);

    const result =  await fetch(`${process.env.httpHost}/user`, {
      method: "post",
      body: formData,
      headers: {
        "x-access-tokens": token
      }
    });
    const response = await result.json();
    console.log(response["message"]);
    Cookies.set('token', response['token']);
    window.location.reload(false);
  }

  return(
    <div className='home_div'>
      <Header title="User Info"/>
      <WarningDialog _open={warningDialogOpen} _close={()=>resetErrorMessageAndCloseDialog()} _message={warningMessage}/>
      <form id='signUpForm' className='table' onSubmit={updateUserInfo}>
        <p className='table-row space-x-2'>
          <label className='table-cell' htmlFor='email'>Email: </label>
          <input className='table-cell my-1 border-2' name='email' type='text' defaultValue={userInfo['email']} required readOnly></input><br/>
        </p>

        <p className='table-row space-x-2'>
          <label className='table-cell' htmlFor='name'>Name: </label>
          <input className='table-cell my-1 border-2' name='name' type='text' defaultValue={userInfo['name']} required></input><br/>
        </p>

        <p className='table-row space-x-2'>
          <label className='table-cell' htmlFor='upsName'>UPS Name: </label>
          <input className='table-cell my-1 border-2' name='upsName' type='text' defaultValue={userInfo['upsName']}></input><br/>
        </p>

        <p className='table-row space-x-2'>
          <label className='table-cell' htmlFor='location_x'>Location X: </label>
          <input className='table-cell my-1 border-2' name='location_x' type='number'  defaultValue={userInfo['location_x']} required></input><br/>
        </p>

        <p className='table-row space-x-2'>
          <label className='table-cell' htmlFor='location_y'>Location Y: </label>
          <input className='table-cell my-1 border-2' name='location_y' type='number'  defaultValue={userInfo['location_y']} required></input><br/>
        </p>
        
        <p className='table-row space-x-2'>
          <label className='table-cell' htmlFor='password'>Password: </label>
          <input className='table-cell my-1 border-2' name='password' type='password'  defaultValue={userInfo['password']} required></input><br/>
        </p>

        <p className='table-row space-x-2'>
          <label className='table-cell' htmlFor='confirm_password'>Confirm Password: </label>
          <input className='table-cell my-1 border-2' name='confirm_password' type='password'  defaultValue={userInfo['password']} required></input><br/>
        </p>
      </form>

      <button form='signUpForm' type='submit' className='btn'>
          Update
        </button>
    </div>
  );
}

export async function getServerSideProps({req, rep}){
  const token = req.cookies.token || null;

  const result =  await fetch(`${process.env.httpHost}/user`, {
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
  
  const body = await result.json();
  return {
    props: {
      body: body,
    }
  }
}

