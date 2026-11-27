import { Routes, Route } from "react-router-dom"
import Header from "./components/Header"
import Footer from "./components/Footer"
import RequireAuth from "./components/RequireAuth"
import Home from "./pages/Home"
import { Browse, ProductDetail, InfoPage } from "./pages/BasicPages"
import { AccountPage, LoginPage, OwnerPage, RegisterPage } from "./pages/AuthPages"

export default function App() {
  return <>
    <Header/>
    <Routes>
      <Route path="/" element={<Home/>}/>
      <Route path="/browse" element={<Browse/>}/>
      <Route path="/product/:id" element={<ProductDetail/>}/>
      <Route path="/login" element={<LoginPage/>}/>
      <Route path="/register" element={<RegisterPage/>}/>
      <Route element={<RequireAuth/>}>
        <Route path="/account" element={<AccountPage/>}/>
      </Route>
      <Route element={<RequireAuth roles={["OWNER"]}/>}>
        <Route path="/owner" element={<OwnerPage/>}/>
      </Route>
      <Route path="/list-item" element={<InfoPage title="Your things can go places." text="Owner onboarding is not open yet. Owner accounts are provisioned through a trusted verification process; public registration cannot grant owner permissions."/>}/>
      <Route path="/about" element={<InfoPage title="A more useful way to share." text="RentNearby is building a neighbourhood-first rental marketplace, starting in Bengaluru."/>}/>
      <Route path="/contact" element={<InfoPage title="Let's talk." text="Support channels will be published before the pilot opens."/>}/>
      <Route path="/terms" element={<InfoPage title="Terms of use" text="Draft terms will be reviewed before any public transactions are enabled."/>}/>
      <Route path="/privacy" element={<InfoPage title="Privacy matters." text="A complete privacy notice will be published before collecting account or personal data."/>}/>
      <Route path="/safety" element={<InfoPage title="Trust is part of the product." text="Verification, handover evidence, dispute handling and clear policies are being designed before launch."/>}/>
      <Route path="*" element={<InfoPage title="Page not found" text="The page you're looking for doesn't exist."/>}/>
    </Routes>
    <Footer/>
  </>
}
