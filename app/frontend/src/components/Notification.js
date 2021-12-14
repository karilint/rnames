import React from 'react'
import './notification.css'

export const Notification = ({ notification }) => {
    if (notification === undefined || notification === null) {
        return <></>
    }

    let className

    switch (notification.type) {
        case 'error':
            className = 'w3-panel w3-border w3-red w3-border-dark-gray'
            break
        case 'information':
            className = 'w3-panel w3-border w3-blue w3-border-dark-gray'
            break
    }

    return (
        <div className={className}>
            <p>{notification.message}</p>
        </div>
    )
}
