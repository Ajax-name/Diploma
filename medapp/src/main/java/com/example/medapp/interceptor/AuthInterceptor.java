package com.example.medapp.interceptor;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;
import org.springframework.web.servlet.ModelAndView;

@Component
public class AuthInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {

        // Разрешаем доступ к страницам логина и регистрации без проверки
        String uri = request.getRequestURI();
        if (uri.equals("/login.html") || uri.equals("/register.html") || uri.equals("/login") || uri.equals("/register")) {
            return true;
        }

        // Проверяем наличие пользователя в сессии
        HttpSession session = request.getSession(false);
        if (session != null && session.getAttribute("user") != null) {
            return true;
        }

        // Иначе редиректим на страницу логина
        response.sendRedirect("/frontend/login.html");
        return false;
    }

    @Override
    public void postHandle(HttpServletRequest request, HttpServletResponse response,
                           Object handler, ModelAndView modelAndView) throws Exception {
        // Можно добавить логику после выполнения контроллера, если нужно
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
                                Object handler, Exception ex) throws Exception {
        // Можно добавить логику после завершения запроса
    }
}
