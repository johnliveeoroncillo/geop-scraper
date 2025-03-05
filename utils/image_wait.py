from selenium.webdriver.support.ui import WebDriverWait

def wait_for_angular(driver, timeout=20):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script(
            "return (window.angular !== undefined) && "
            "(angular.element(document.body).injector() !== undefined) && "
            "(angular.element(document.body).injector().get('$http').pendingRequests.length === 0);"
        )
    )