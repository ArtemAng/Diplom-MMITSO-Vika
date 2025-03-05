import { useForm } from 'react-hook-form';
import { TextField, Button, Box, Typography } from '@mui/material';

const RegistrationForm = () => {
  const { register, handleSubmit, formState: { errors }, watch } = useForm();
  const onSubmit = (data) => console.log(data);

  const password = watch('password');

  return (
    <Box sx={{ maxWidth: 400, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" gutterBottom>Регистрация</Typography>

      <form onSubmit={handleSubmit(onSubmit)}>
        <TextField
          fullWidth
          label="Имя пользователя"
          {...register('username', { required: 'Имя пользователя обязательно' })}
          error={!!errors.username}
          helperText={errors.username?.message}
          margin="normal"
        />

        <TextField
          fullWidth
          label="Имя"
          {...register('first_name', { required: 'Имя обязательно' })}
          error={!!errors.first_name}
          helperText={errors.first_name?.message}
          margin="normal"
        />

        <TextField
          fullWidth
          label="Фамилия"
          {...register('last_name', { required: 'Фамилия обязательна' })}
          error={!!errors.last_name}
          helperText={errors.last_name?.message}
          margin="normal"
        />

        <TextField
          fullWidth
          label="Email"
          type="email"
          {...register('email', {
            required: 'Email обязателен',
            pattern: {
              value: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
              message: 'Некорректный email'
            }
          })}
          error={!!errors.email}
          helperText={errors.email?.message}
          margin="normal"
        />

        <TextField
          fullWidth
          label="Пароль"
          type="password"
          {...register('password', { required: 'Пароль обязателен', minLength: { value: 6, message: 'Минимум 6 символов' } })}
          error={!!errors.password}
          helperText={errors.password?.message}
          margin="normal"
        />

        <TextField
          fullWidth
          label="Подтверждение пароля"
          type="password"
          {...register('confirmPassword', {
            required: 'Подтверждение пароля обязательно',
            validate: (value) => value === password || 'Пароли не совпадают'
          })}
          error={!!errors.confirmPassword}
          helperText={errors.confirmPassword?.message}
          margin="normal"
        />

        <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
          Зарегистрироваться
        </Button>
      </form>
    </Box>
  );
};

export default RegistrationForm;
