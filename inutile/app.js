var Loan = React.createClass({
	componentWillMount(){
  	// var loanData = $.get("http://inpersontransfers.herokuapp.com/requests/8/")
      // .then(function(data){console.log(data);})
      var loanData = {
        amount: 12,
        latitude: 0,
        id: 8,
        paid: false,
        requestee:"jenblight",
        requester: "jenblight",
        uber_link: "uber://action=setPickup&client_id=RXjda_RLc1B5KhzoOB9nDnkaGJOkJAmv&dropoff[latitude]=0.0[longitude]=0.0&dropoff[nickname]=Your%20Friend&product_id=a1111c8c-c720-46c3-8534-2fcdd730040d"
      }
      console.log (loanData)
    this.setState({
      requestee: loanData.requestee,
    	requester: loanData.requester,
      amount: loanData.amount,
      link: loanData.uber_link
    })
  },
  getInitialState(){
  	return {
    	name: '',
      amount: '',
      link: ''
    }
  },
  render(){
  	return (
      <div className="loan">
        <div className="loanDesc">
          {this.state.requestee} owes {this.state.requester}
         </div>
        <div className="loanAmount">{this.state.amount}</div>
      <a href={this.state.link} className="payback">PAY THEM BACK</a></div>
    )
  }
})

ReactDOM.render(
  <Loan />,
  document.getElementById('container')
);
