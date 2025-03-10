import logo from './logo.svg';
import './App.css';
import Dashboard from './components/dashboard/Dashboard';
import AppTheme from './shared-theme/AppTheme';
import {
  chartsCustomizations,
  dataGridCustomizations,
  datePickersCustomizations,
  treeViewCustomizations,
} from './theme/customizations';

const xThemeComponents = {
  ...chartsCustomizations,
  ...dataGridCustomizations,
  ...datePickersCustomizations,
  ...treeViewCustomizations,
};

function App() {
  return (
    <div className="App">
      <AppTheme themeComponents={xThemeComponents}>
        <Dashboard />
      </AppTheme>
    </div>
  );
}

export default App;
