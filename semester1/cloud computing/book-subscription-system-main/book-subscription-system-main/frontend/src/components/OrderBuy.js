import {WrapperID} from "./WrapperID";
import {useState} from "react";
import {useNavigate, useParams} from 'react-router-dom';

export const OrderBuy = () => {

    const user_params = useParams();
    let user_id = parseInt(user_params.user_id);

    const [book_id, setBookId] = useState('');
    const [quantity, setQuantity] = useState('');
    const [price, setPrice] = useState([]);
    const [book_name, setBookName] = useState([]);
    const navigate = useNavigate();

    const submit = async e => {
        e.preventDefault();

        const response = await fetch(`http://localhost:5000/buy`, {
            method: 'POST',
            body: JSON.stringify({
                user_id, quantity,book_id
        }),
        });
        const content = await response.json();
        setPrice(content["price"]);
        setBookName(content["book_name"]);

        await navigate(-1);
    }

    return <WrapperID>
        <form className="mt-3" onSubmit={submit}>

            <div className="form-floating pb-3">
                <input type="number" className="form-control" placeholder="book_id"
                       onChange={e => setBookId(e.target.value)}
                />
                <label>book_id</label>
            </div>

            <div className="form-floating pb-3">
                <input type="number" className="form-control" placeholder="quantity"
                       onChange={e => setQuantity(e.target.value)}
                />
                <label>quantity</label>
            </div>

            <button className="w-100 btn btn-lg btn-primary" onSubmit={submit}>Submit</button>
        </form>
    </WrapperID>
}