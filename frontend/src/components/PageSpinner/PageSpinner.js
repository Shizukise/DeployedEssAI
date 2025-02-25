import './PageSpinner.css'

const PageSpinner = () => {
    return (
        <div className="spinner-border m-5" role="status">
            <span className="visually-hidden">Loading...</span>
        </div>
    )
}

export default PageSpinner